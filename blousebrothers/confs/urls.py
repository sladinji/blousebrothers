# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url
from django.core.urlresolvers import reverse_lazy
from django.views.generic.base import RedirectView

from . import views
from . import crud

from jchart.views import ChartView
from blousebrothers.users.charts import MeanBarChart
mb_chart = MeanBarChart()

urlpatterns = [
    url(regex=r'^$',
        view=RedirectView.as_view(url=reverse_lazy('catalogue:index'), permanent=True),
        name='root'
        ),
    url(
        r'^charts/mean_chart/(?P<user_id>\d+)/(?P<friend_id>\d+)?$',
        ChartView.from_chart(mb_chart),
        name='mb_chart'
    ),
    # URL pattern for the ConferenceHomeView
    url(
        r'^dashboard$',
        view=views.ConferenceHomeView.as_view(),
        name='home'
    ),
    # URL pattern for the ConferenceListView
    url(
        r'^mes_dossiers/?$',
        view=views.ConferenceListView.as_view(),
        name='list'
    ),

    # URL pattern for the TestUpdateView
    url(
        regex=r'^dossier/(?P<slug>[\w.@+-]+)$',
        view=views.TestUpdateView.as_view(),
        name='test'
    ),
    # URL pattern for the TestResetView
    url(
        regex=r'^dossier/(?P<slug>[\w.@+-]+)/resettest$',
        view=views.TestResetView.as_view(),
        name='test_reset'
    ),

    # URL pattern for the TestUpdateView
    url(
        regex=r'^dossier/(?P<slug>[\w.@+-]+)/resultats$',
        view=views.TestResult.as_view(),
        name='result'
    ),


    # URL pattern for the ConferenceDetailView
    url(
        regex=r'^dossier/(?P<slug>[\w.@+-]+)/$',
        view=views.ConferenceDetailView.as_view(),
        name='detail'
    ),

    # URL pattern for the ConferenceUpdateView
    url(
        regex=r'^creation/(?P<slug>[\w.@+-]+)/update$',
        view=views.ConferenceUpdateView.as_view(),
        name='update'
    ),
    url(
        regex=r'^~create/(?P<slug>[\w.@+-]+)/update$',
        view=RedirectView.as_view(pattern_name='confs:update', permanent=True),
        name='oldupdate'
    ),
    url(
        regex=r'^creation/(?P<slug>[\w.@+-]+)/delete$',
        view=views.ConferenceDeleteView.as_view(),
        name='delete'
    ),
    url(
        regex=r'^creation/(?P<slug>[\w.@+-]+)/final$',
        view=views.ConferenceFinalView.as_view(),
        name='final'
    ),
    # URL pattern for the ConferenceUpdateView
    url(
        regex=r'^creation/$',
        view=views.ConferenceCreateView.as_view(),
        name='create'
    ),
    url(
        regex=r'^creation/(?P<slug>[\w.@+-]+)/edit$',
        view=views.ConferenceEditView.as_view(),
        name='edit'
    ),
    url(r'^dossiers_faits/?$',
        views.BuyedConferenceListView.as_view(),
        name='my_confs'),

    url(r'^switch_correction$',
        view=views.ajax_switch_correction,
        name="switch_correction",
        ),
    url(r'^switch_for_sale$',
        view=views.ajax_switch_for_sale,
        name="switch_for_sale",
        ),


    #   #####  ############  #####   #
    #    ###   # CRUD API #   ###    #
    #     #    ############    #     #

    url(r'^crud/conference/?$',
        crud.ConferenceCRUDView.as_view(),
        name='conference_crud_view'),

    url(r'^crud/studentconference/?$',
        crud.StudentConferenceCRUDView.as_view(),
        name='student_conference_crud_view'),

    url(r'^crud/test/?$',
        crud.TestCRUDView.as_view(),
        name='test_crud_view'),

    url(r'^crud/test_answer/?$',
        crud.TestAnswerCRUDView.as_view(),
        name='test_answer_crud_view'),

    url(r'^conference/upload_image/(?P<conference_id>[0-9]+)?$',
        crud.UploadConferenceImage.as_view(),
        name='up_conf_img'),

    url(r'^crud/conferenceimage/?$',
        crud.ConferenceImageCRUDView.as_view(),
        name='conferenceimage_crud_view'),

    url(r'^crud/studentconferenceimage/?$',
        crud.StudentConferenceImageCRUDView.as_view(),
        name='student_conferenceimage_crud_view'),

    url(r'^crud/question/?$',
        crud.QuestionCRUDView.as_view(),
        name='question_crud_view'),

    url(r'^crud/predval/?$',
        crud.PredictionValidationCRUDView.as_view(),
        name='prediction_validation_crud_view'),

    url(r'^crud/studentquestion/?$',
        crud.StudentQuestionCRUDView.as_view(),
        name='student_question_crud_view'),

    url(r'^crud/questionimage/?$',
        crud.QuestionImageCRUDView.as_view(),
        name='questionimage_crud_view'),

    url(r'^crud/studentquestionimage/?$',
        crud.StudentQuestionImageCRUDView.as_view(),
        name='student_questionimage_crud_view'),

    url(r'^crud/questionexplainationimage/?$',
        crud.QuestionImageExplainationCRUDView.as_view(),
        name='questionexplainationimage_crud_view'),

    url(r'^crud/studentquestionexplainationimage/?$',
        crud.StudentQuestionImageCRUDView.as_view(),
        name='student_questionexplainationimage_crud_view'),

    url(r'^crud/answer/?$',
        crud.AnswerCRUDView.as_view(),
        name='answer_crud_view'),

    url(r'^crud/studentanswer/?$',
        crud.StudentAnswerCRUDView.as_view(),
        name='student_answer_crud_view'),

    url(r'^crud/studentanswerimage/?$',
        crud.StudentAnswerImageCRUDView.as_view(),
        name='student_answerimage_crud_view'),

    url(r'^crud/answerimage/?$',
        crud.AnswerImageCRUDView.as_view(),
        name='answerimage_crud_view'),

    url(r'^answer/upload_image/(?P<answer_id>[0-9]+)?$',
        crud.UploadAnswerImage.as_view(),
        name='up_answer_img'),

    url(r'^question/upload_image/(?P<question_id>[0-9]+)?$',
        crud.UploadQuestionImage.as_view(),
        name='up_question_img'),

    url(r'^question/upload_explainationimage/(?P<question_id>[0-9]+)?$',
        crud.UploadQuestionExplainationImage.as_view(),
        name='up_question_expimg'),
]
