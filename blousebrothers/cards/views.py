from django.views.generic import (
    ListView,
    UpdateView,
    CreateView,
)
from .models import Card
from .forms import CreateCardForm


class CreateCardView(CreateView):
    model = Card
    form_class = CreateCardForm


class UpdateCardView(UpdateView):
    model = Card


class ListCardView(ListView):
    model = Card
