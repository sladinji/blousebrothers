from django.forms.models import inlineformset_factory, ModelForm

from .models import(
        Conference,
        Question,
)

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
        extra = 1,
        can_order=True, can_delete= True,
)
