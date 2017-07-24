from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic import (
    ListView,
    UpdateView,
    CreateView,
    DetailView,
    RedirectView,
)
from .models import Card, Deck
from .forms import CreateCardForm, UpdateCardForm


def choose_new_card(request):
    # choose a new card never done by user
    new_card = Card.objects.exclude(
        id__in=Deck.objects.filter(student=request.user).values_list('card', flat=True)
    ).first()
    # if all card are already done choose the oldest and hardest one
    if not new_card:
        new_card = Card.objects.filter(
            deck__student=request.user
        ).order_by(
            'deck__nb_views',
            '-deck__difficulty',
            'deck__modified',
        ).first()
    return new_card


def bookmark_card(request, card_id):
    """
    Bookmark given card by updating user deck with given card.
    Other revision of the card are parent or brothers of the given card.
    """
    bcard = Card.objects.get(card_id)
    Deck.objects.filter(Q(card__in=bcard.children) | Q(card=bcard.parent)).update(card=bcard)
    return JsonResponse(True)


class CreateCardView(CreateView):
    model = Card
    form_class = CreateCardForm

    def get_success_url(self):
        return reverse('cards:list')


class UpdateCardView(UpdateView):
    model = Card
    form_class = UpdateCardForm

    def get_context_data(self, **kwargs):
        class Mock:
            card=None

        context = super().get_context_data(**kwargs)
        mock = Mock()
        mock.card = context['object']
        context.update(object=mock)
        return context

    def form_valid(self, form):
        """
        Create a new version if current user is not the author
        """
        if form.instance.author != self.request.user:
            form.instance.parent = Card.objects.get(id=form.instance.pk)
            form.instance.pk = None
            form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('cards:revision', kwargs={'slug': self.object.slug})


class RevisionRedirectView(RedirectView):
    """
    Root url of card app, reached by clicking on revision link.
    Choose a card a redirect to revision view.
    """

    def get_redirect_url(self):
        new_card = choose_new_card(self.request)
        return reverse('cards:revision', kwargs={'slug': new_card.slug})


class RevisionView(DetailView):
    template_name = "cards/revision.html"
    model = Deck

    def get_object(self, queryset=None):
        card = Card.objects.get(slug=self.kwargs['slug'])
        obj, _ = self.model.objects.get_or_create(card=card, student=self.request.user)
        return obj

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if 'easy' in request.POST:
            self.object.difficulty = 0
        elif 'average' in request.POST:
            self.object.difficulty = 1
        elif 'hard' in request.POST:
            self.object.difficulty = 2
        self.object.save()
        new_card = choose_new_card(request)
        return redirect(reverse('cards:revision', kwargs={'slug': new_card.slug}))


class ListCardView(ListView):
    model = Card

    def get_queryset(self):
        qry = self.model.objects.all()
        if self.request.GET.get('q', False):
            qry = qry.filter(
                Q(title__icontains=self.request.GET['q']) |
                Q(content__icontains=self.request.GET['q']) |
                Q(section__icontains=self.request.GET['q'])
            )
        return qry.all()
