import random
from os.path import splitext, basename
from datetime import timedelta, datetime
from django.utils import timezone
from django.db.models import Q
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from image_cropping import ImageCropField, ImageRatioField
from model_utils import Choices

DURATION_CHOICES = (
    (timedelta(minutes=10), _('10 min')),
    (timedelta(minutes=20), _('20 min')),
    (timedelta(minutes=45), _('45 min')),
)


class Deck(models.Model):
    """
    User <--> Cards M2M relation with notes
    """
    DIFFICULTY_CHOICES = Choices(
        (0, 'EASY', _('Facile')),
        (1, 'MIDDLE', _('Moyen')),
        (2, 'HARD', _('Dur')),
    )
    student = models.ForeignKey("users.User", verbose_name=_("Étudiant"), on_delete=models.CASCADE,
                                related_name="deck", blank=False, null=False)
    card = models.ForeignKey("Card", verbose_name=_("Fiche"), on_delete=models.CASCADE,
                             related_name="deck", blank=False, null=False)
    difficulty = models.PositiveIntegerField(_("Difficulté"), choices=DIFFICULTY_CHOICES, default=1)
    created = models.DateTimeField(auto_now_add=True)
    column = models.PositiveIntegerField(default=0)
    wake_up = models.DateTimeField(default=datetime(2000, 1, 1))
    modified = models.DateTimeField(auto_now=True)
    nb_views = models.IntegerField(default=0)
    trashed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        """
        Increment nb_views
        """
        self.nb_views += 1
        return super().save(*args, **kwargs)


class Tag(models.Model):
    name = models.CharField(_("Tags"), max_length=256, blank=False, null=False)

    def __str__(self):
        return self.name


class ForUserQuerySet(models.query.QuerySet):
    """
    MANAGER TO MANAGE USER ACCESS RIGHTS
    """
    def for_user(self, user):
        """
        Card accessible by user
        """
        if user.is_authenticated():
            return self.filter(
                Q(author=user) | Q(public=True) | Q(author__in=[
                    x.from_user for x in user.has_friendship.filter(share_cards=True)
                ])
            )
        else:
            return self.filter(public=True)


class ForUserManager(models.Manager):
    def get_query_set(self):
            return ForUserQuerySet(self.model)

    def for_user(self, *args, **kwargs):
            return self.get_query_set().for_user(*args, **kwargs)


class Card(models.Model):
    """
    Fiche de revision
    """
    objects = ForUserManager()
    specialities = models.ManyToManyField('confs.Speciality', verbose_name=("Specialities"),
                                          related_name='cards', blank=True)
    items = models.ManyToManyField('confs.Item', verbose_name=_("Items"),
                                   related_name='cards', blank=True)
    tags = models.ManyToManyField('Tag', verbose_name=("Tags"),
                                  related_name='cards', blank=True)
    content = models.TextField(_('Réponse'), blank=True, null=True)
    parent = models.ForeignKey("Card", verbose_name=_("Original"), on_delete=models.SET_NULL,
                               related_name="children", blank=True, null=True)
    author = models.ForeignKey("users.User", verbose_name=_("Auteur"), on_delete=models.SET_NULL,
                               related_name="created_cards", blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    public = models.BooleanField(default=False)
    free = models.BooleanField(default=True)
    anki_pkg = models.ForeignKey("AnkiPackage", verbose_name=_("Package Anki"), on_delete=models.SET_NULL,
                                 related_name="cards", blank=True, null=True)
    anki_id = models.BigIntegerField(_("id in anki package"), null=True, default=None)

    def family(self, user):
        """
        Return family accessible by user.
        """
        parent = self.parent or self
        return [parent] + list(parent.children.filter(
            Q(author__isnull=True) | Q(author=user) | Q(public=True)
        ).order_by("created"))

    def get_absolute_url(self):
        return reverse('cards:revision', args=[self.id])

    @property
    def root(self):
        return self if not self.parent else self.parent

    def get_root_absolute_url(self):
        parent = self.parent or self
        return reverse('cards:revision', args=[parent.id])

    @staticmethod
    def new_cards(user, search=None, specialities=None, items=None):
        qs = Card.objects.for_user(user).filter(
            parent__isnull=True,
        ).exclude(  # exclude cards already done
                  id__in=user.deck.values_list(
                      'card__id', flat=True,
                  )
        ).exclude(  # exclude sibling cards
            id__in=user.deck.filter(
                card__parent__isnull=False
            ).values_list(
                'card__parent', flat=True,
            )
        )
        if specialities:
            qs = qs.filter(specialities__in=specialities)
        if items:
            qs = qs.filter(items__in=items)
        if search:
            qs = qs.filter(
                Q(content__icontains=search) |
                Q(specialities__name__icontains=search) |
                Q(tags__name__icontains=search) |
                Q(items__name__icontains=search)
            )
        return qs.all()


def apkg_directory_path(apkg, filename):
    return 'anki/{0}/{1}'.format(apkg.owner.username, filename)


class AnkiPackage(models.Model):
    owner = models.ForeignKey("users.User", verbose_name=_("Auteur"), on_delete=models.SET_NULL,
                              related_name="anki_packages", blank=False, null=True)
    date = models.DateField(_("Date created"), auto_now_add=True)
    file = models.FileField(_("Fichier"), upload_to=apkg_directory_path)

    def filename(self):
        return basename(self.file.name)


def anki_image_directory_path(anki_image, filename):
    return '{0}/{1}'.format(
        splitext(anki_image.package.file.name)[0],
        filename)


class AnkiImage(models.Model):
    package = models.ForeignKey("AnkiPackage", verbose_name=_("Package"), on_delete=models.CASCADE,
                                related_name="images", blank=False, null=False)
    image = ImageCropField(_("Image"), upload_to=anki_image_directory_path, max_length=255,)
    cropping = ImageRatioField('image', '430x360', free_crop=True)


class CardsPreference(models.Model):
    student = models.ForeignKey("users.User", verbose_name=_("Étudiant"), on_delete=models.CASCADE,
                                related_name="cards_preference", blank=False, null=False)
    session_duration = models.DurationField(_("Niveau"), max_length=10, choices=DURATION_CHOICES,
                                            blank=False, default=DURATION_CHOICES[0][0], null=False)


def card_image_directory_path(card_image, filename):
    return '{0.owner.username}/cards_images/{1}'.format(card_image, filename)


class CardImage(models.Model):
    owner = models.ForeignKey("users.User", verbose_name=_("Image"), on_delete=models.CASCADE,
                              related_name="card_images", blank=False, null=False)
    image = ImageCropField(_("Image"), upload_to=card_image_directory_path, max_length=255)
    cropping = ImageRatioField('image', '430x360', allow_fullsize=True)


class SessionOverException(Exception):
    pass


class Session(models.Model):
    """
    Revision session
    """
    student = models.ForeignKey("users.User", verbose_name=_("Étudiant"), on_delete=models.CASCADE,
                                related_name="sessions", blank=False, null=False)
    date_created = models.DateTimeField(_("Date created"), auto_now_add=True)
    date_modified = models.DateTimeField(_("Date modified"), auto_now=True)
    selected_duration = models.DurationField()
    effective_duration = models.DurationField(default=timedelta())
    finished = models.BooleanField(default=False)
    cards = models.ManyToManyField('Card', verbose_name=("Fiches"), related_name='sessions', blank=True)
    specialities = models.ManyToManyField('confs.Speciality', verbose_name=("Specialities"),
                                          related_name='sessions', blank=True)
    items = models.ManyToManyField('confs.Item', verbose_name=_("Items"),
                                   related_name='sessions', blank=True)
    tags = models.ManyToManyField('Tag', verbose_name=("Tags"),
                                  related_name='sessions', blank=True)
    revision = models.BooleanField(default=False)
    search = models.TextField(_('Rechercher'), blank=True, null=True)

    def __str__(self):
        return '<Session {} revision: {}>'.format(self.pk, self.revision)

    def check_is_not_over(self):
        """
        Raise SessionOverException if required.
        """
        self.save()  # update self.date_modified on save
        if self.selected_duration < self.date_modified - self.date_created:
            raise SessionOverException()
        return False

    @property
    def waiting_cards(self):
        qs = self.student.deck.filter(
            wake_up__lt=timezone.now(),
            trashed=False,
        )
        if self.specialities.all():
            qs = qs.filter(card__specialities__in=self.specialities.all())
        if self.items.all():
            qs = qs.filter(card__items__in=self.items.all())
        if self.tags.all():
            qs = qs.filter(card__items__in=self.items.all())
        if self.search:
            qs = qs.filter(
                Q(content__icontains=self.search) |
                Q(specialities__name__icontains=self.search) |
                Q(tags__name__icontains=self.search) |
                Q(items__name__icontains=self.search)
            )
        return qs.order_by('wake_up')

    @property
    def matching_cards(self):
        """
        Apply session preference filter to a Card queryset
        """
        qs = Card.objects.for_user(self.student)
        if self.search:
            qs = qs.filter(
                Q(content__icontains=self.search) |
                Q(specialities__name__icontains=self.search) |
                Q(tags__name__icontains=self.search) |
                Q(items__name__icontains=self.search)
            )
        if self.specialities.all():
            qs = qs.filter(specialities__in=self.specialities.all())
        if self.items.all():
            qs = qs.filter(items__in=self.items.all())
        qs = qs.exclude(
            id__in=[card.id for card in self.cards.all()]
        )
        if not qs.count():
            """All cards have been seen in this session."""
            raise SessionOverException()
        return qs

    @property
    def new_cards(self):
        """
        Return a queryset with all card never done by user
        according to session preferences.
        """
        return Card.new_cards(self.student,
                              self.search,
                              self.specialities.all(),
                              self.items.all(),
                              )

    def choose_revision_card(self):
        if self.waiting_cards.count():  # randomly look into waiting cards
            new_card = random.choice(self.waiting_cards[:100]).card
            return new_card
        else:
            raise SessionOverException()


@receiver(pre_save, sender=Session)
def update_effective_duration(sender, **kwargs):
    """
    Method to update effective_duration before save.
    """
    instance = kwargs.get('instance')
    if instance.date_modified and instance.date_created:
        duration = instance.date_modified - instance.date_created
        instance.effective_duration = duration if duration < instance.selected_duration else instance.selected_duration
