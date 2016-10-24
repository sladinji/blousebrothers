from __future__ import unicode_literals, absolute_import

import re
import os
import uuid
from decimal import Decimal

from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.dispatch import receiver
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.safestring import mark_safe
from oscar.models.fields import AutoSlugField


class ConfManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted=False)


class AdminConfManager(models.Manager):
    """
    Admin manager return all objects.
    """
    def get_queryset(self):
        return super().get_queryset()


class Conference(models.Model):
    objects = ConfManager()
    all_objects = AdminConfManager()

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
    summary = models.CharField(_('Esprit du dossier'), blank=False, null=False, max_length=140,
                               help_text=_('Ex: "dossier très pointu et monothématique sur la fibrillation auriculaire"'
                                           ' ou "dossier transversal de révisions classiques sur lupus et grossesse" '))
    statement = models.TextField(_('Énoncé*'), blank=True, null=True)
    items = models.ManyToManyField('Item', verbose_name=("Items"), related_name='conferences',
                                   help_text=_('Ne sélectionner que les items abordés de manière '
                                               '<strong>significative</strong> dans votre dossier')
                                   )
    specialities = models.ManyToManyField('Speciality', verbose_name=_('Spécialités'), related_name='conferences')
    edition_progress = models.PositiveIntegerField(_("Progression"), default=0)
    price = models.DecimalField(_("Prix de vente"), max_digits=6, decimal_places=2,
                                default=Decimal(0.50),
                                validators=[MinValueValidator(Decimal(0.50)),
                                            MaxValueValidator(100)],
                                help_text=mark_safe(
                                    _("Une commission de 10% du prix de vente + 10 centimes est soustraite à chaque vente réalisée. <a href='/cgu'>Voir nos conditions générales d'utilisation</a>."))
                                )
    deleted = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse('confs:detail', kwargs={'slug': self.slug})

    def get_all_txt(self):
        """
        Return a string with all text of conference.
        """
        txt = ' '.join([x.lower() if x else "" for x in (self.summary, self.title, self.statement)])
        for q in self.questions.all():
            txt += q.question.lower() if q.question else ''
            for a in q.answers.all():
                txt += a.explaination.lower() if a.explaination else ''
        return txt

    def set_suggested_items(self):
        txt = self.get_all_txt()
        for item in Item.objects.all():
            for kw in item.kwords.all():
                if re.search(r'[^\w]'+kw.value+r'[^\w]', txt):
                    self.items.add(item)
                    break


def conf_directory_path(conf_image, filename):
    return '{0}/conf_{1}/{2}'.format(conf_image.conf.owner.username,
                                     conf_image.conf.id,
                                     "{}{}".format(uuid.uuid5(uuid.NAMESPACE_DNS,
                                                              filename
                                                              ),
                                                   os.path.splitext(filename)[-1]
                                                   )
                                     )


class ConferenceImage(models.Model):
    image = models.ImageField(_("Image"), upload_to=conf_directory_path, max_length=255)
    date_created = models.DateTimeField(_("Date created"), auto_now_add=True)
    caption = models.CharField(_("Légende"), max_length=200, blank=True)
    index = models.PositiveIntegerField(_("Ordre"), default=0)
    conf = models.ForeignKey('Conference', related_name='images')


@receiver(models.signals.pre_delete, sender=ConferenceImage)
def auto_delete_conference_image_on_delete(sender, instance, **kwargs):
    """Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.image:
        instance.image.delete()


class Item(models.Model):
    """
    National item exam
    """
    name = models.CharField("Item", max_length=128, blank=False, null=False)
    number = models.IntegerField(_("Numéro"), blank=False, null=False)

    def __str__(self):
        return self.name


class ItemKeyWord(models.Model):
    item = models.ForeignKey('Item', related_name='kwords')
    value = models.CharField('Valeur', max_length=128, blank=False)

    def __str__(self):
        return self.value


class Speciality(models.Model):
    name = models.CharField(_("Matière"), max_length=128, blank=False, null=False)

    def __str__(self):
        return self.name


class Question(models.Model):
    question = models.TextField(_("Enoncé"), blank=False, null=False, max_length=64)
    conf = models.ForeignKey('Conference', related_name='questions', verbose_name=_("Conference"))
    index = models.PositiveIntegerField(_("Ordre"), default=0)
    coefficient = models.PositiveIntegerField(_("Coéfficient"), default=1)

    def is_valid(self):
        one_good = len([a for a in self.answers.all() if a.answer and a.correct]) >= 1
        all_filled = len([a for a in self.answers.all() if a.answer]) == 5
        return one_good and all_filled


def answer_image_directory_path(answer_image, filename):
    return '{0}/conf_{1}/answers/{2}'.format(answer_image.question.conf.owner.username,
                                             answer_image.question.conf.id,
                                             "{}{}".format(uuid.uuid5(uuid.NAMESPACE_DNS,
                                                                      filename
                                                                      ),
                                                           os.path.splitext(filename)[-1]
                                                           )
                                             )


class Answer(models.Model):
    class Meta:
        ordering = ['index']
    question = models.ForeignKey(Question, related_name="answers")
    answer = models.TextField(_("Proposition"), blank=True, null=True)
    explaination = models.TextField(_("Explication"), blank=True, null=True)
    explaination_image = models.ImageField(_("Image"), upload_to=answer_image_directory_path, max_length=255,
                                           blank=True, null=True)
    correct = models.BooleanField(_("Correct"), default=False)
    ziw = models.BooleanField(_("Zéro si erreur"), default=False)
    index = models.PositiveIntegerField(_("Ordre"), default=0)


@receiver(models.signals.pre_delete, sender=Answer)
def auto_delete_answer_image_on_delete(sender, instance, **kwargs):
    """Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.explaination_image:
        instance.explaination_image.delete()


def question_image_directory_path(question_image, filename):
    return '{0}/conf_{1}/questions/{2}'.format(question_image.question.conf.owner.username,
                                               question_image.question.conf.id,
                                               "{}{}".format(uuid.uuid5(uuid.NAMESPACE_DNS,
                                                                        filename
                                                                        ),
                                                             os.path.splitext(filename)[-1]
                                                             )
                                               )


class QuestionImage(models.Model):
    image = models.ImageField(_("Image"), upload_to=question_image_directory_path, max_length=255)
    date_created = models.DateTimeField(_("Date created"), auto_now_add=True)
    caption = models.CharField(_("Libellé"), max_length=200, blank=True)
    index = models.PositiveIntegerField(_("Ordre"), default=0)
    question = models.ForeignKey('Question', related_name='images')


@receiver(models.signals.pre_delete, sender=QuestionImage)
def auto_delete_question_image_on_delete(sender, instance, **kwargs):
    """Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.image:
        instance.image.delete()

