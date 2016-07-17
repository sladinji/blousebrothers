# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from oscar.models.fields import AutoSlugField


class Conference(models.Model):
    TYPE_CHOICES = (
        ('QI', _('QI')),
        ('DCP', _('DCP')),
    )

    def __str__(self):
        return self.title

    owner = models.ForeignKey('users.User', blank=False, null=False)
    """ Owner/creator """
    date_created = models.DateTimeField(_("Date created"), auto_now_add=True)
    title = models.CharField(_('Titre'), blank=False, null=False, max_length=64)
    slug = AutoSlugField(_('Slug'), max_length=128, unique=True,
                         populate_from='title')
    abstract = models.TextField(_('Résumé'), blank=False, null=False, max_length=140)
    type = models.CharField(_("Type"), max_length=10, choices=TYPE_CHOICES,
                            blank=False, default='QI')
    items = models.ManyToManyField('Item', verbose_name=_("Items"), related_name='conferences')
    specialities = models.ManyToManyField('Speciality', verbose_name=_('Spécialités'), related_name='conferences')

    def get_absolute_url(self):
        return reverse('confs:detail', kwargs={'slug': self.slug})


class Item(models.Model):
    """
    National item exam
    """
    name = models.CharField(_("Item"), max_length=128, blank=False, null=False)
    number = models.IntegerField(_("Numéro"), blank=False, null=False)

    def __str__(self):
        return self.name


class Speciality(models.Model):
    name = models.CharField(_("Matière"), max_length=128, blank=False, null=False)

    def __str__(self):
        return self.name


class Question(models.Model):
    question = models.TextField(_("Enoncé"), max_length=256, blank=False, null=False)
    conf = models.ForeignKey('Conference', related_name='questions', verbose_name=_("Conference"))
    order = models.PositiveIntegerField(_("Ordre"), default=0)
    answer = models.CharField(_("Réponse"), max_length=256, blank=False, null=False)
    explaination = models.CharField(_("Explication"), max_length=256, blank=True, null=True)
    correct = models.BooleanField(_("Correct"), default=False)

class QuestionImage(models.Model):

    image = models.ImageField(_("Image"), upload_to=settings.OSCAR_IMAGE_FOLDER, max_length=255)
    date_created = models.DateTimeField(_("Date created"), auto_now_add=True)
    caption = models.CharField(_("Libellé"), max_length=200, blank=True)
    order = models.PositiveIntegerField(_("Ordre"), default=0)
    question = models.ForeignKey('Question', related_name='images')
