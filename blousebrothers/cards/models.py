import random
from datetime import timedelta, datetime
from django.utils import timezone
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.utils.translation import ugettext_lazy as _
from blousebrothers.confs.models import AutoSlugField
from django.db.models import Q
from django.core.urlresolvers import reverse
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

    def save(self, *args, **kwargs):
        """
        Increment nb_views
        """
        self.nb_views += 1
        return super().save(*args, **kwargs)


class Tag(models.Model):
    name = models.CharField(_("Tags"), max_length=256, blank=False, null=False)


class Card(models.Model):
    """
    Fiche de revision
    """
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
    slug = AutoSlugField(_('Slug'), max_length=256, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    public = models.BooleanField(default=False)
    free = models.BooleanField(default=True)

    def family(self, user):
        """
        Return family accessible by user.
        """
        parent = self.parent or self
        return [parent] + list(parent.children.filter(
            Q(author__isnull=True) | Q(author=user) | Q(public=True)
        ).order_by("created"))

    def get_absolute_url(self):
        return reverse('cards:revision', args=[self.slug])

    @property
    def root(self):
        return self if not self.parent else self.parent

    def get_root_absolute_url(self):
        parent = self.parent or self
        return reverse('cards:revision', args=[parent.slug])


class CardsPreference(models.Model):
    student = models.ForeignKey("users.User", verbose_name=_("Étudiant"), on_delete=models.CASCADE,
                                related_name="cards_preference", blank=False, null=False)
    session_duration = models.DurationField(_("Niveau"), max_length=10, choices=DURATION_CHOICES,
                                            blank=False, default=DURATION_CHOICES[0][0], null=False)


class SessionOverException(Exception):
    pass


class Session(models.Model):
    """
    Revision session
    """
    student = models.ForeignKey("users.User", verbose_name=_("Étudiant"), on_delete=models.CASCADE,
                                related_name="sessions", blank=False, null=False)
    date_created = models.DateField(_("Date created"), auto_now_add=True)
    date_modified = models.DateField(_("Date modified"), auto_now=True)
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

    def __str__(self):
        return '<Session [{}] revision: {}>'.format(self.pk, self.revision)

    def is_over(self, specialities, items, revision):
        """
        Close session and raise SessionOverException if required.
        """
        self.save()  # update self.date_modified on save
        if self.selected_duration < self.date_modified - self.date_created \
                or specialities and specialities != self.specialities \
                or items and items != self.items \
                or revision and not self.revision:
            self.finished = True
            self.save()
            return True
        return False

    def filter(self, qs):
        """
        Apply session preference filter to a Card queryset
        """
        if self.specialities.all():
            qs = qs.filter(specialities__in=self.specialities.all())
        if self.items.all():
            qs = qs.filter(items__in=self.items.all())
        return qs

    @property
    def waiting_cards(self):
        qs = self.student.deck.filter(
            wake_up__lt=timezone.now()
        )
        if self.specialities.all():
            qs = qs.filter(card__specialities__in=self.specialities.all())
        if self.items.all():
            qs = qs.filter(card__items__in=self.items.all())
        return qs.order_by('wake_up')

    def choose_revision_card(self):
        if self.waiting_cards.count():  # randomly look into waiting cards
            new_card = random.choice(self.waiting_cards[:100]).card
            return new_card
        else:  # randomly choose in the most 20 ready
            new_card = random.choice(self.student.deck.order_by('wake_up').all()[:20]).card
            return new_card


@receiver(pre_save, sender=Session)
def update_effective_duration(sender, **kwargs):
    """
    Method to update effective_duration before save.
    """
    instance = kwargs.get('instance')
    if instance.date_modified and instance.date_created:
        duration = instance.date_modified - instance.date_created
        instance.effective_duration = duration if duration < instance.selected_duration else instance.selected_duration
