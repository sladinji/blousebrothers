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
    # choose a new original card never done by user
    new_card = Card.objects.filter(
        parent__isnull=True,
    ).exclude(
        id__in=Deck.objects.filter(student=request.user).values_list('card', flat=True),
    ).first()
    # check if user have done card of this family
    if new_card and Deck.objects.filter(student=request.user,
                                        card_id__in=get_family(new_card),
                                        ).exists():
        new_card = None
    # if all card are already done choose the oldest and hardest one
    if not new_card:
        new_card = Card.objects.filter(
            deck__student=request.user,
        ).order_by(
            'deck__modified',
            '-deck__difficulty',
        ).first()
    return new_card


def bookmark_card(request, card_id):
    """
    Bookmark given card by updating user deck with given card.
    Other revision of the card are parent or brothers of the given card.
    """
    bcard = Card.objects.get(pk=card_id)
    Deck.objects.filter(
        Q(card__in=bcard.children.all()) | Q(card=bcard.parent),
        student=request.user
    ).update(card=bcard)
    return JsonResponse({'success': True})


class CreateCardView(CreateView):
    model = Card
    form_class = CreateCardForm

    def get_success_url(self):
        return reverse('cards:list')


class UpdateCardView(UpdateView):
    model = Card
    form_class = UpdateCardForm

    def get_context_data(self, **kwargs):
        """
        Share same template as Revision view. Because Revision view use Deck
        as model, we mock Deck model with another class.
        """
        class Mock:
            card = None

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
            current_card = Card.objects.get(id=form.instance.pk)
            form.instance.parent = current_card.parent or current_card
            form.instance.pk = None
            form.instance.author = self.request.user
            obj = form.save()
            # Must save obj before setting m2m attributes
            obj.items.set(current_card.items.all())
            obj.specialities.set(current_card.specialities.all())
            obj.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('cards:revision', kwargs={'slug': self.object.slug})


def get_family(card):
    """
    Return all family members of given card.
    """
    parent = card.parent or card
    return [parent] + list(parent.children.all().order_by("created"))


class RevisionRedirectView(RedirectView):
    """
    Root url of card app, reached by clicking on revision link.
    Choose a card a redirect to revision view.
    """

    def get_redirect_url(self, *args, **kwargs):
        new_card = choose_new_card(self.request)
        return reverse('cards:revision', kwargs={'slug': new_card.slug})


class RevisionNextCardView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        current_card = Card.objects.get(pk=args[0])
        family = get_family(current_card)
        new_card = family[(family.index(current_card) + 1) % len(family)]
        return reverse('cards:revision', kwargs={'slug': new_card.slug, 'dsp_card_on_load':True})


class RevisionPreviousCardView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        current_card = Card.objects.get(pk=args[0])
        family = get_family(current_card)
        new_card = family[(family.index(current_card) - 1) % len(family)]
        return reverse('cards:revision', kwargs={'slug': new_card.slug, 'dsp_card_on_load':True})


class RevisionView(DetailView):
    template_name = "cards/revision.html"
    model = Deck
    is_favorite = False

    def get_object(self, queryset=None):
        """
        Only one card by family in user's deck. If a sibling card is present
        in user's deck, we return this deck instance with the requested card.
        Otherwise we create a new desk instance with request card.
        """
        card = Card.objects.get(slug=self.kwargs['slug'])
        obj = Deck.objects.filter(
            student=self.request.user,
            card__in=get_family(card),
        ).exclude(
            card=card,
        ).first()
        if obj:
            obj.card = card
            self.is_favorite = False
        else:
            obj, _ = Deck.objects.get_or_create(card=card, student=self.request.user)
            self.is_favorite = True
        return obj

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context.update(is_favorite=self.is_favorite)
        context.update(dsp_card_on_load=self.kwargs['dsp_card_on_load'] == "True")
        return context

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
