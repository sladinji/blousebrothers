from django.forms.models import inlineformset_factory, ModelForm

from .models import(
        Conference,
        Question,
)


class QuestionInline(ModelForm):
    class Meta:
        model = Question
        fields = '__all__'


class ConferenceForm(ModelForm):
    class Meta:
        model = Conference
        exclude = ['owner']

# inlineformset_factory creates a Class from a parent model (Contact)
# to a child model (Address)
QuestionFormSet = inlineformset_factory(
        Conference,
        Question,
        exclude=['owner', 'order',],
        can_order=True, can_delete= True,
)
