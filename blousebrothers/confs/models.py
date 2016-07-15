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
        return self.name

    def get_absolute_url(self):
        return reverse('confs:detail', kwargs={'uuid': self.uuid})

    owner = models.ForeignKey('users.User', blank=False, null=False)
    """ Owner/creator """
    date_created = models.DateTimeField(_("Date created"), auto_now_add=True)
    title = models.CharField(_('Titre'), blank=False, null=False, max_length=64)
    slug = AutoSlugField(_('Slug'), max_length=128, unique=True,
                         populate_from='title')
    abstract = models.TextField(_('Résumé'), blank=False, null=False, max_length=140)
    type = models.CharField(_("Type"), max_length=10, choices=TYPE_CHOICES,
                            blank=False, default='QI')
    items = models.ManyToManyField('Item', verbose_name=_("Items"))
    specialities = models.ManyToManyField('Speciality', verbose_name=_('Spécialités'))

    def get_absolute_url(self):
        return reverse('confs:detail', kwargs={'slug': self.slug})

class Item(models.Model):
    """
    National item exam
    """
    name = models.CharField(_("Nom"), max_length=128, blank=False, null=False)
    number = models.IntegerField(_("Numéro"), blank=False, null=False)


class Speciality(models.Model):
    name = models.CharField(_("Nom"), max_length=128, blank=False, null=False)


class Question(models.Model):
    label = models.TextField(_("Enoncé"), max_length=256, blank=False, null=False)
    conf = models.ForeignKey('Conference', related_name='questions', verbose_name=_("Conference"))
    order = models.PositiveIntegerField(_("Ordre"), default=0)


class Answer(models.Model):
    label = models.CharField(_("Réponse"), max_length=256, blank=False, null=False)
    why = models.CharField(_("Explication"), max_length=256, blank=True, null=True)
    correct = models.BooleanField(_("Correct"), default=False)
    question = models.ForeignKey('Question', related_name='answers', verbose_name=_("Question"))


class QuestionImage(models.Model):

    image = models.ImageField(_("Image"), upload_to=settings.OSCAR_IMAGE_FOLDER, max_length=255)
    date_created = models.DateTimeField(_("Date created"), auto_now_add=True)
    caption = models.CharField(_("Libellé"), max_length=200, blank=True)
    order = models.PositiveIntegerField(_("Ordre"), default=0)

admin.site.register(Item)
admin.site.register(Speciality)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(QuestionImage)
