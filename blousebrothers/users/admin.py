# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from datetime import datetime, timedelta
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django import forms
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.safestring import mark_safe
from .models import User, University
from blousebrothers.confs.models import Conference
from django_csv_exports.admin import CSVExportAdmin
from hijack_admin.admin import HijackUserAdminMixin

class MyUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User


class MyUserCreationForm(UserCreationForm):

    error_message = UserCreationForm.error_messages.update({
        'duplicate_username': 'This username has already been taken.'
    })

    class Meta(UserCreationForm.Meta):
        model = User

    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages['duplicate_username'])


class FinishedButNotForSaleFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('"on attend quoi pour rendre accessible ?"')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'finished'

    def lookups(self, request, model_admin):
        return (
            ('100', _('Dossier complet mais non accessible aux étudiants')),
        )

    def queryset(self, request, queryset):
        if self.value() == '100':
            return queryset.filter(created_confs__edition_progress__lt=100,
                                   created_confs__for_sale=False,
                                   )


class EditionProgressListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('dossier en cours')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'decade'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('1w', _('depuis une semaine')),
            ('1m', _('depuis un mois')),
            ('xm', _("depuis plus d'un mois")),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        last_week = datetime.now()-timedelta(days=7)
        last_month = datetime.now()-timedelta(days=30)
        if self.value() == '1w':
            return queryset.filter(created_confs__edition_progress__lt=100,
                                   created_confs__date_created__gte=last_week,
                                   )
        if self.value() == '1m':
            return queryset.filter(created_confs__edition_progress__lt=100,
                                   created_confs__date_created__lt=last_week,
                                   created_confs__date_created__gte=last_month,
                                   )
        if self.value() == 'xm':
            return queryset.filter(created_confs__edition_progress__lt=100,
                                   created_confs__date_created__lt=last_month,
                                   )


@admin.register(User)
class MyUserAdmin(AuthUserAdmin, HijackUserAdminMixin, CSVExportAdmin):

    form = MyUserChangeForm
    add_form = MyUserCreationForm
    fieldsets = (
            ('Profil', {'fields': ('is_conferencier', 'wanabe_conferencier',
            'wanabe_conferencier_date', 'degree', 'mobile')}),
    ) + AuthUserAdmin.fieldsets

    def created_confs(self):
        html = ""
        for obj in Conference.objects.filter(owner__id=self.id):
            html += '<p><a href="{}">{} ({}%)</a></p>'.format(
                obj.get_absolute_url(), obj.title, obj.edition_progress)
        return mark_safe(html)

    def social_avatar(self):
        html=""
        if self.socialaccount_set.all() :
            avatar = self.socialaccount_set.first().get_avatar_url()
            html = '<img style="width:150px;height:150px;border-radius:50%;" src="{}">'.format(avatar)
        return mark_safe(html)

    list_display = ('username', social_avatar,  'date_joined', 'degree', 'email', 'is_conferencier', created_confs,
                    'hijack_field',)
    csv_fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'mobile']
    search_fields = ['username', 'name', 'first_name', 'last_name', 'email', 'mobile', 'phone']
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'is_conferencier',
                   'wanabe_conferencier', 'city', "degree", 'date_joined',
                   EditionProgressListFilter, FinishedButNotForSaleFilter)

admin.site.register(University)
