from django.core.urlresolvers import reverse
from django.views.generic import (
    ListView,
    UpdateView,
    CreateView,
    DetailView,
)
from .models import Card
from .forms import CreateCardForm


class CreateCardView(CreateView):
    model = Card
    form_class = CreateCardForm

    def get_success_url(self):
        return reverse('cards:list')


class UpdateCardView(UpdateView):
    model = Card
    form_class = CreateCardForm


class DetailCardView(UpdateView):
    model = Card


class ListCardView(ListView):
    model = Card

    def get_queryset(self):
        qry = self.model.objects.all()
        if self.request.GET.get('q', False):
            qry = qry.filter(title_tmp__icontains=self.request.GET['q'])

        return qry.all()