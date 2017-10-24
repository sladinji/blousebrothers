from itertools import chain

from django import forms
from django.forms.models import ModelForm
from django_select2.forms import ModelSelect2MultipleWidget
from djng.styling.bootstrap3.forms import Bootstrap3FormMixin
from blousebrothers.users.models import User
from .models import Relationship, Group


class FriendsWidget(ModelSelect2MultipleWidget):
    def label_from_instance(self, user):
        return "{username} ({first_name} {last_name})".format(**user.__dict__)


class FriendsForm(forms.Form, Bootstrap3FormMixin):
    friends = forms.ModelMultipleChoiceField(
        label="",
        queryset=User.objects.all(),
        widget=FriendsWidget(
            model=User,
            search_fields=['username__icontains',
                           'first_name__icontains',
                           'last_name__icontains',
                           'email__icontains', ]
        ),
        required=True,
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        self.fields['friends'].queryset = User.objects.exclude(
            id__in=[x.id for x in user.friends.all()]
        )


class SharingForm(ModelForm, Bootstrap3FormMixin):

    class Meta:
        model = Relationship
        fields = ['share_cards', 'share_results', 'share_confs']


class GroupForm(forms.Form, Bootstrap3FormMixin):
    groups = forms.ModelMultipleChoiceField(
        label="Nom ou ville du groupe",
        queryset=Group.objects.all(),
        widget=ModelSelect2MultipleWidget(
            model=Group,
            search_fields=['name__icontains', ]
        ),
        required=True,
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        self.fields['groups'].queryset = Group.objects.exclude(
            id__in=[x.id for x in list(chain(user.groups.all(), user.groups_moderator.all()))]
        )


class GroupInvitForm(ModelForm, Bootstrap3FormMixin):
    class Meta:
        model = Relationship
        fields = []

    emails = forms.CharField(
        widget=forms.Textarea,
        label="Emails",
        help_text="Copie colle une liste d'emails, on s'occupe du reste ;)",
    )
