# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from .models import User, University


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


@admin.register(User)
class MyUserAdmin(AuthUserAdmin):
    form = MyUserChangeForm
    add_form = MyUserCreationForm
    fieldsets = (
            ('Profil', {'fields': ('is_conferencier', 'wanabe_conferencier',
            'wanabe_conferencier_date', 'degree', 'mobile')}),
    ) + AuthUserAdmin.fieldsets
    list_display = ('username', 'name', 'is_superuser', 'is_conferencier', 'wanabe_conferencier')
    search_fields = ['name', 'is_conferencier', 'wanabe_conferencier']
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'is_conferencier',
    'wanabe_conferencier')

admin.site.register(University)
