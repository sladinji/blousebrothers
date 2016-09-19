# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
import os

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.dispatch import receiver
from oscar.models.fields import AutoSlugField


class Conference(models.Model):
    TYPE_CHOICES = (
        ('DCP', _('DCP')),
        ('QI', _('QI')),
    )

    def __str__(self):
        return self.title

    owner = models.ForeignKey('users.User', blank=False, null=False)
    """ Owner/creator """
    date_created = models.DateTimeField(_("Date created"), auto_now_add=True)
    title = models.CharField(_('Titre'), blank=False, null=False, max_length=64)
    type = models.CharField(_("Type"), max_length=10, choices=TYPE_CHOICES,
                            blank=False, default='DP')
    slug = AutoSlugField(_('Slug'), max_length=128, unique=True,
                         populate_from='title')
    summary = models.CharField(_('Résumé'), blank=False, null=False, max_length=140,
                               help_text=_("Ce résumé doit décrire le contenu de la conférence en moins de 140 caractères."))
    statement = models.TextField(_('Énoncé'), blank=False, null=False)
    items = models.ManyToManyField('Item', verbose_name=("Items"), related_name='conferences')
    specialities = models.ManyToManyField('Speciality', verbose_name=_('Spécialités'), related_name='conferences')
    edition_progress = models.PositiveIntegerField(_("Progression"), default=0)

    def get_absolute_url(self):
        return reverse('confs:update', kwargs={'slug': self.slug})



class ConferenceImage(models.Model):
    image = models.ImageField(_("Image"), upload_to=settings.OSCAR_IMAGE_FOLDER, max_length=255)
    date_created = models.DateTimeField(_("Date created"), auto_now_add=True)
    caption = models.CharField(_("Légende"), max_length=200, blank=True)
    index = models.PositiveIntegerField(_("Ordre"), default=0)
    conf = models.ForeignKey('Conference', related_name='images')


# These two auto-delete files from filesystem when they are unneeded:
@receiver(models.signals.post_delete, sender=ConferenceImage)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)


class Item(models.Model):
    """
    National item exam
    """
    name = models.CharField("Item", max_length=128, blank=False, null=False)
    number = models.IntegerField(_("Numéro"), blank=False, null=False)

    def __str__(self):
        return "%s - %s" % (self.number, self.name)


class Speciality(models.Model):
    name = models.CharField(_("Matière"), max_length=128, blank=False, null=False)

    def __str__(self):
        return self.name


class Question(models.Model):
    question = models.TextField(_("Enoncé"), blank=False, null=False, max_length=64)
    conf = models.ForeignKey('Conference', related_name='questions', verbose_name=_("Conference"))
    index = models.PositiveIntegerField(_("Ordre"), default=0)

    def is_valid(self):
        one_good = len([a for a in self.answers.all() if a.answer and a.correct]) >= 1
        all_filled = len([a for a in self.answers.all() if a.answer ]) == 5
        return one_good and all_filled


class Answer(models.Model):
    question = models.ForeignKey(Question, related_name="answers")
    answer = models.CharField(_("Proposition"), max_length=256, blank=True, null=True)
    explaination = models.CharField(_("Explication"), blank=True, max_length=256, null=True)
    explaination_image = models.ImageField(_("Image"), upload_to=settings.OSCAR_IMAGE_FOLDER, max_length=255,
                                           blank=True, null=True)
    correct = models.BooleanField(_("Correct"), default=False)
    ziw = models.BooleanField(_("Zéro si erreur"), default=False)
    index = models.PositiveIntegerField(_("Ordre"), default=0)

class QuestionImage(models.Model):
    image = models.ImageField(_("Image"), upload_to=settings.OSCAR_IMAGE_FOLDER, max_length=255)
    date_created = models.DateTimeField(_("Date created"), auto_now_add=True)
    caption = models.CharField(_("Libellé"), max_length=200, blank=True)
    index = models.PositiveIntegerField(_("Ordre"), default=0)
    question = models.ForeignKey('Question', related_name='images')
