from django.db import models
from django.utils.translation import ugettext_lazy as _
from blousebrothers.confs.models import AutoSlugField
from django.db.models import Q
from django.core.urlresolvers import reverse


class Deck(models.Model):
    """
    User <--> Cards M2M relation with notes
    """
    student = models.ForeignKey("users.User", verbose_name=_("Étudiant"), on_delete=models.CASCADE,
                                related_name="deck", blank=False, null=False)
    card = models.ForeignKey("Card", verbose_name=_("Fiche"), on_delete=models.CASCADE,
                             related_name="deck", blank=False, null=False)
    difficulty = models.PositiveIntegerField(_("Difficulté"), default=1)
    created = models.DateTimeField(auto_now_add=True)
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
    LEVEL_CHOICES = (
        ('EASY', _('Facile')),
        ('MIDDLE', _('Moyen')),
        ('HARD', _('Dur')),
    )
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
    level = models.CharField(_("Level"), max_length=10, choices=LEVEL_CHOICES,
                             blank=False, default='MIDDLE')
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
