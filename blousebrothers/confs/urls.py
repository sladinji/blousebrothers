# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views
from . import crud

urlpatterns = [
    # URL pattern for the ConferenceListView
    url(
        regex=r'^$',
        view=views.ConferenceListView.as_view(),
        name='list'
    ),

    # URL pattern for the TestUpdateView
    url(
        regex=r'^(?P<slug>[\w.@+-]+)/workinout$',
        view=views.TestUpdateView.as_view(),
        name='test'
    ),
    # URL pattern for the TestResetView
    url(
        regex=r'^(?P<slug>[\w.@+-]+)/resettest$',
        view=views.TestResetView.as_view(),
        name='test_reset'
    ),

    # URL pattern for the TestUpdateView
    url(
        regex=r'^(?P<slug>[\w.@+-]+)/result$',
        view=views.TestResult.as_view(),
        name='result'
    ),
    # URL pattern for the RefundView
    url(
        regex=r'^(?P<slug>[\w.@+-]+)/askrefund$',
        view=views.RefundView.as_view(),
        name='ask_refund'
    ),


    # URL pattern for the ConferenceDetailView
    url(
        regex=r'^(?P<slug>[\w.@+-]+)/$',
        view=views.ConferenceDetailView.as_view(),
        name='detail'
    ),

    # URL pattern for the ConferenceUpdateView
    url(
        regex=r'^(?P<slug>[\w.@+-]+)/update$',
        view=views.ConferenceUpdateView.as_view(),
        name='update'
    ),
    url(
        regex=r'^(?P<slug>[\w.@+-]+)/delete$',
        view=views.ConferenceDeleteView.as_view(),
        name='delete'
    ),
    url(
        regex=r'^(?P<slug>[\w.@+-]+)/final$',
        view=views.ConferenceFinalView.as_view(),
        name='final'
    ),
    # URL pattern for the ConferenceUpdateView
    url(
        regex=r'^~create/$',
        view=views.ConferenceCreateView.as_view(),
        name='create'
    ),
    url(
        regex=r'^(?P<slug>[\w.@+-]+)/edit$',
        view=views.ConferenceEditView.as_view(),
        name='edit'
    ),
    url(r'^gottowork/?$',
        views.BuyedConferenceListView.as_view(),
        name='my_confs'),


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

    url(r'^comment/question/?$',
        crud.StudentQuestionCommentView.as_view(),
        name='question_comment'),

    url(r'^crud/conferenceimage/?$',
        crud.ConferenceImageCRUDView.as_view(),
        name='conferenceimage_crud_view'),

    url(r'^crud/studentconferenceimage/?$',
        crud.StudentConferenceImageCRUDView.as_view(),
        name='student_conferenceimage_crud_view'),

    url(r'^crud/question/?$',
        crud.QuestionCRUDView.as_view(),
        name='question_crud_view'),

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
