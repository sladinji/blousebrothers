from __future__ import unicode_literals, absolute_import

import ast
import re
import os
import uuid
from decimal import Decimal
from datetime import date
import logging

from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.core.validators import int_list_validator

from autoslug import AutoSlugField as RealAutoSlugField
from image_cropping import ImageCropField, ImageRatioField

logger = logging.getLogger(__name__)


class AutoSlugField(RealAutoSlugField):
    # XXX: Work around https://bitbucket.org/neithere/django-autoslug/issues/34/django-migrations-fail-if-autoslugfield
    def deconstruct(self):
        name, path, args, kwargs = super(AutoSlugField, self).deconstruct()
        if 'manager' in kwargs:
            del kwargs['manager']
        return name, path, args, kwargs


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

    owner = models.ForeignKey('users.User', blank=False, null=False,
                              related_name="created_confs")
    """ Owner/creator """
    date_created = models.DateTimeField(_("Date created"), auto_now_add=True)
    title = models.CharField(_('Titre'), blank=False, null=False, max_length=64)
    type = models.CharField(_("Type"), max_length=10, choices=TYPE_CHOICES,
                            blank=False, default='DP')
    slug = AutoSlugField(_('Slug'), max_length=128, unique=True,
                         populate_from='title', manager=all_objects)
    summary = models.CharField(_('Esprit du dossier'), blank=False, null=False, max_length=140,
                               help_text=_('Ex: "dossier très pointu et monothématique sur la fibrillation auriculaire"'
                                           ' ou "dossier transversal de révisions classiques sur lupus et grossesse" '))
    statement = models.TextField(_('Énoncé*'), blank=True, null=True)
    items = models.ManyToManyField('Item', verbose_name=("Items"), related_name='conferences',
                                   help_text=_('Ne sélectionner que les items abordés de manière '
                                               '<strong>significative</strong> dans votre dossier'),
                                   blank=True,
                                   )
    specialities = models.ManyToManyField('Speciality', verbose_name=_('Spécialités'), related_name='conferences',
                                          blank=True)
    edition_progress = models.PositiveIntegerField(_("Progression"), default=0)
    price = models.DecimalField(_("Prix de vente"), max_digits=6, decimal_places=2,
                                default=Decimal(0.50),
                                help_text=mark_safe(
                                    _(""))
                                )
    deleted = models.BooleanField(default=False)
    for_sale = models.BooleanField(_("Accessible"), default=False,
                                   help_text=_("Un sujet accessible apparaitra dans les recherches et pourra être "
                                               "acheté au prix que vous avez fixé."
                                               )
                                   )
    date_tuto = models.DateTimeField(_("Accès gratuit aux étudiants de ma ville le "),
                                     blank=True, null=True)

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

    @property
    def icono(self):
        """
        Number of images available in this conference.
        """
        conf = self.images.count()
        question = QuestionImage.objects.filter(question__conf=self).count()
        answer = AnswerImage.objects.filter(answer__question__conf=self).count()
        qei = QuestionExplainationImage.objects.filter(question__conf=self).count()
        return conf + question + answer + qei


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
    image = ImageCropField(_("Image"), upload_to=conf_directory_path, max_length=255,)
    cropping = ImageRatioField('image', '430x360', free_crop=True)
    date_created = models.DateTimeField(_("Date created"), auto_now_add=True)
    caption = models.CharField(_("Légende"), max_length=200, blank=True)
    index = models.PositiveIntegerField(_("Ordre"), default=0)
    conf = models.ForeignKey('Conference', related_name='images')


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
    question = models.TextField(_("Enoncé"), blank=False, null=False)
    conf = models.ForeignKey('Conference', related_name='questions', verbose_name=_("Conference"))
    index = models.PositiveIntegerField(_("Ordre"), default=0)
    coefficient = models.PositiveIntegerField(_("Coéfficient"), default=1)
    explaination = models.TextField(_("Remarque globale pour la correction"), blank=True, null=True)

    def is_valid(self):
        one_good = len([a for a in self.answers.all() if a.answer and a.correct]) >= 1
        all_filled = len([a for a in self.answers.all() if a.answer]) == 5
        return one_good and all_filled

    def __str__(self):
        return str(self.index + 1) + '. ' + self.question[:20] + '...'

    @property
    def good_answers(self):
        return self.answers.filter(correct=True)

    @property
    def bad_answers(self):
        return self.answers.filter(correct=False)

    @property
    def good_index(self):
        return [x.index for x in self.good_answers]

    @property
    def bad_index(self):
        return [x.index for x in self.bad_answers]


class QuestionComment(models.Model):
    question = models.ForeignKey(Question, related_name="comments")
    student = models.ForeignKey('users.User', blank=False, null=False,
                                related_name="comments")
    comment = models.TextField(_("Explication"), blank=True, null=True)
    date_created = models.DateTimeField(_("Date created"), auto_now_add=True)


class Answer(models.Model):
    class Meta:
        ordering = ['index']
    question = models.ForeignKey(Question, related_name="answers")
    answer = models.TextField(_("Proposition"), blank=True, null=True)
    explaination = models.TextField(_("Explication"), blank=True, null=True)
    correct = models.BooleanField(_("Correct"), default=False)
    ziw = models.BooleanField(_("Zéro si erreur"), default=False)
    index = models.PositiveIntegerField(_("Ordre"), default=0)


def answer_image_directory_path(answer_image, filename):
    return '{0}/conf_{1}/answers/{2}'.format(answer_image.answer.question.conf.owner.username,
                                             answer_image.answer.question.conf.id,
                                             "{}{}".format(uuid.uuid5(uuid.NAMESPACE_DNS,
                                                                      filename
                                                                      ),
                                                           os.path.splitext(filename)[-1]
                                                           )
                                             )


class AnswerImage(models.Model):
    image = ImageCropField(_("Image"), upload_to=answer_image_directory_path, max_length=255,)
    cropping = ImageRatioField('image', '430x360', free_crop=True)
    date_created = models.DateTimeField(_("Date created"), auto_now_add=True)
    caption = models.CharField(_("Libellé"), max_length=200, blank=True)
    index = models.PositiveIntegerField(_("Ordre"), default=0)
    answer = models.ForeignKey('Answer', related_name='images')


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
    image = ImageCropField(_("Image"), upload_to=question_image_directory_path, max_length=255,)
    cropping = ImageRatioField('image', '430x360', free_crop=True)
    date_created = models.DateTimeField(_("Date created"), auto_now_add=True)
    caption = models.CharField(_("Libellé"), max_length=200, blank=True)
    index = models.PositiveIntegerField(_("Ordre"), default=0)
    question = models.ForeignKey('Question', related_name='images')


class QuestionExplainationImage(models.Model):
    image = ImageCropField(_("Image"), upload_to=question_image_directory_path, max_length=255,)
    cropping = ImageRatioField('image', '430x360', free_crop=True)
    date_created = models.DateTimeField(_("Date created"), auto_now_add=True)
    caption = models.CharField(_("Libellé"), max_length=200, blank=True)
    index = models.PositiveIntegerField(_("Ordre"), default=0)
    question = models.ForeignKey('Question', related_name='explaination_images')


class Test(models.Model):
    student = models.ForeignKey('users.User', blank=False, null=False,
                                related_name="tests")
    conf = models.ForeignKey('Conference', related_name='tests')
    date_created = models.DateTimeField(_("Date created"), auto_now_add=True)
    progress = models.PositiveIntegerField(_("Progression"), default=0)
    result = models.PositiveIntegerField(_("Résultat"), default=0)
    max_score = models.PositiveIntegerField(_("Résultat"), default=0)
    score = models.DecimalField(_("Résultat"), max_digits=6, decimal_places=2, default=0)
    finished = models.BooleanField(default=False)
    personal_note = models.TextField(_("Remarques personnelles"), blank=True, null=True,
                                     help_text=_("Visible uniquement par toi, note ici les choses "
                                                 "que tu veux retenir, ça pourra également te "
                                                 "permettre de retrouver plus facilement ce dossier."

                                                 )
                                     )
    time_taken = models.TimeField(_("Temps passé"), null=True)

    def set_score(self):
        for t_answer in self.answers.all():
            t_answer.set_score()
        self.max_score = self.answers.aggregate(models.Sum('max_score')).get("max_score__sum")
        self.score = self.answers.aggregate(models.Sum('score')).get("score__sum")
        self.finished = True
        self.save()

    @property
    def fatal_errors(self):
        return [x for ta in self.answers.all() for x in ta.fatals.all()]

    @property
    def nb_errors(self):
        return self.answers.aggregate(models.Sum('nb_errors')).get("nb_errors__sum")


class TestAnswer(models.Model):
    test = models.ForeignKey('Test', related_name='answers')
    question = models.ForeignKey('Question', related_name='test_answers')
    time_taken = models.TimeField(_("Temps passé"), null=True)
    given_answers = models.CharField(_("Réponses"), max_length=30, blank=True,
                                     validators=[int_list_validator])
    """String representing a list of checked answer (ex: "0, 1, 3")"""
    max_score = models.PositiveIntegerField(_("Résultat"), default=0)
    score = models.DecimalField(_("Résultat"), max_digits=6, decimal_places=2, default=0)
    nb_errors = models.PositiveIntegerField(_("Nombre d'erreurs"), default=0)
    fatals = models.ManyToManyField('Answer', verbose_name=("Erreurs graves"))

    def set_score(self):
        self.max_score = self.question.coefficient
        ga = ast.literal_eval(self.given_answers + ',')
        omissions = [ans for ans in self.question.good_answers if ans.index not in ga]
        errors = [ans for ans in self.question.bad_answers if ans.index in ga]
        bga = omissions + errors
        self.nb_errors = len(bga)
        fatals = [x for x in bga if x.ziw]
        if fatals:
            self.fatals.add(*fatals)
        if sorted(ga) == sorted(self.question.good_index):
            self.score = self.max_score
        elif len(bga) > 2 or fatals:
            self.score = 0
        elif len(bga) == 2:
            self.score = Decimal(0.2 * self.question.coefficient)
        elif len(bga) == 1:
            self.score = Decimal(0.5 * self.question.coefficient)
        self.save()

class SubscriptionType(models.Model):
    name = models.CharField(_('Nom'), blank=False, null=False, max_length=64)
    description = models.TextField(_('Description'), blank=True, null=True)
    nb_month = models.IntegerField(_('Durée'), blank=True, null=True)
    price = models.DecimalField(_("Prix"), max_digits=6, decimal_places=2, default=0)

class Subscription(models.Model):
    user = models.ForeignKey('users.User', blank=False, null=False, related_name="subs")
    type = models.ForeignKey('SubscriptionType', related_name="subs", blank=False, null=False)
    date_created = models.DateField(_("Date created"), auto_now_add=True)
    date_over = models.DateField(_("Date created"), null=False)
    price_paid = models.DecimalField(_("Vendu pour"), max_digits=6, decimal_places=2, default=0)


    @property
    def is_past_due(self):
        return date.today() > self.date_over
