# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [
    # URL pattern for the ConferenceListView
    url(
        regex=r'^$',
        view=views.ConferenceListView.as_view(),
        name='list'
    ),

    # URL pattern for the ConferenceRedirectView
    url(
        regex=r'^~redirect/$',
        view=views.ConferenceRedirectView.as_view(),
        name='redirect'
    ),

    # URL pattern for the ConferenceDetailView
    url(
        regex=r'^(?P<slug>[\w.@+-]+)/$',
        view=views.ConferenceDetailView.as_view(),
        name='detail'
    ),

    # URL pattern for the ConferenceUpdateView
    url(
        regex=r'^(?P<slug>[\w.@+-]+)/~update$',
        view=views.ConferenceUpdateView.as_view(),
        name='update'
    ),
    # URL pattern for the ConferenceUpdateView
    url(
        regex=r'^~create/$',
        view=views.ConferenceCreateView.as_view(),
        name='create'
    ),
    url(
        regex=r'^(?P<slug>[\w.@+-]+)/~edit$',
        view=views.ConferenceEditView.as_view(),
        name='edit'
    ),
    url(r'^crud/conference/?$',
        views.ConferenceCRUDView.as_view(),
        name='conference_crud_view'),

    url(r'^crud/conferenceimage/?$',
        views.ConferenceImageCRUDView.as_view(),
        name='conferenceimage_crud_view'),

    url(r'^crud/question/?$',
        views.QuestionCRUDView.as_view(),
        name='question_crud_view'),

    url(r'^crud/questionimage/?$',
        views.QuestionImageCRUDView.as_view(),
        name='questionimage_crud_view'),

    url(r'^crud/answer/?$',
        views.AnswerCRUDView.as_view(),
        name='answer_crud_view'),

    url(r'^wanabe_conferencier/?$',
        views.HandleConferencierRequest.as_view(),
        name='wanabe_conferencier'),

    url(r'^question/upload_image/(?P<question_id>[0-9]+)$',
        views.UploadQuestionImage.as_view(),
        name='up_q_img'),
]
