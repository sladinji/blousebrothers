from django.db import models
from django.utils.translation import ugettext_lazy as _
from blousebrothers.confs.models import AutoSlugField


class Section(models.Model):
    """
    Section of a chapter
    """
    name = models.CharField(_("Section"), max_length=256, blank=False, null=False)


class LessonTitle(models.Model):
    """
    Lesson Title
    """
    name = models.CharField(_("Titre du cours"), max_length=256, blank=False, null=False)


class Deck(models.Model):
    """
    User <--> Cards M2M relation with notes
    """
    student = models.ForeignKey("users.User", verbose_name=_("Étudiant"), on_delete=models.CASCADE,
                                related_name="classeur", blank=False, null=False)
    card = models.ForeignKey("Card", verbose_name=_("Fiche"), on_delete=models.CASCADE,
                             related_name="classeur", blank=False, null=False)
    difficulty = models.PositiveIntegerField(_("Difficulté"), default=1)


class Card(models.Model):
    """
    Fiche de revision
    """
    specialities = models.ManyToManyField('confs.Speciality', verbose_name=("Specialities"),
                                          related_name='cards', blank=True)
    items = models.ManyToManyField('confs.Item', verbose_name=_("Items"),
                                   related_name='cards', blank=True)
    section = models.ForeignKey('Section', verbose_name=_("Chapitre"), on_delete=models.SET_NULL,
                                related_name='cards', blank=True, null=True)
    section_tmp = models.CharField(_("Chapitre"), max_length=256, blank=False, null=False)
    title = models.ForeignKey('LessonTitle', verbose_name=_("Titre du cours"), on_delete=models.SET_NULL,
                              related_name='cards', blank=True, null=True)
    title_tmp = models.CharField(_("Titre du cours"), max_length=256, blank=False, null=False)
    content = models.TextField(_('Contenu'), blank=True, null=True)
    parent = models.ForeignKey("Card", verbose_name=_("Original"), on_delete=models.SET_NULL,
                               related_name="childs", blank=True, null=True)
    author = models.ForeignKey("users.User", verbose_name=_("Auteur"), on_delete=models.SET_NULL,
                               related_name="created_cards", blank=True, null=True)
    slug = AutoSlugField(_('Slug'), max_length=256, unique=True, populate_from='content')
