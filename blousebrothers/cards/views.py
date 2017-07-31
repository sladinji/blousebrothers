from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
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
    TemplateView,
)

from chartit import DataPool, Chart

from blousebrothers.auth import BBLoginRequiredMixin
from .models import Card, Deck
from .forms import CreateCardForm, UpdateCardForm


def choose_new_card(request):
    """
    Hot point.
    """
    # choose a new original card never done by user
    new_card = Card.objects.filter(
        parent__isnull=True,
    ).exclude(
        id__in=Deck.objects.filter(student=request.user).values_list('card', flat=True),
    ).first()
    # check if user have done card of this family
    if new_card and Deck.objects.filter(student=request.user,
                                        card_id__in=new_card.family(request.user),
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
    Ajax view.
    Bookmark given card by updating user deck with given card.
    Other revision of the card are parent or brothers of the given card.
    """
    bcard = Card.objects.get(pk=card_id)
    Deck.objects.filter(
        Q(card__in=bcard.children.all()) | Q(card=bcard.parent),
        student=request.user
    ).update(card=bcard)
    return JsonResponse({'success': True})


class RevisionPermissionMixin(BBLoginRequiredMixin, UserPassesTestMixin):

    def test_func(self):
        if not self.request.user.is_authenticated():
            False
        if self.request.user.is_superuser:
            return True
        self.object = self.get_object()
        card = self.object.card
        return card.author is None or card.author == self.request.user or card.public

    def handle_no_permission(self):
        if not self.request.user.is_authenticated():
            return BBLoginRequiredMixin.handle_no_permission(self)
        raise PermissionDenied


class CreateCardView(RevisionPermissionMixin, CreateView):
    model = Card
    form_class = CreateCardForm

    def get_success_url(self):
        return reverse('cards:list')


class UpdateCardView(RevisionPermissionMixin, UpdateView):
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
        bb = self.request.user.username == "BlouseBrothers"
        if not bb and form.instance.author != self.request.user:
            current_card = Card.objects.get(id=form.instance.pk)
            form.instance.parent = current_card.parent or current_card
            form.instance.pk = None
            form.instance.author = self.request.user
            obj = form.save()
            # Must save obj before setting m2m attributes
            obj.items.set(current_card.items.all())
            obj.specialities.set(current_card.specialities.all())
            obj.save()
            bookmark_card(self.request, obj.pk)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('cards:revision', kwargs={'slug': self.object.slug})


class RevisionRedirectView(BBLoginRequiredMixin, RedirectView):
    """
    Root url of card app, reached by clicking on revision link.
    Choose a card a redirect to revision view.
    """

    def get_redirect_url(self, *args, **kwargs):
        new_card = choose_new_card(self.request)
        return reverse('cards:revision', kwargs={'slug': new_card.slug})


class RevisionNextCardView(BBLoginRequiredMixin, RedirectView):
    step = 1

    def get_redirect_url(self, *args, **kwargs):
        current_card = Card.objects.get(pk=args[0])
        family = current_card.family(self.request.user)
        new_card = family[(family.index(current_card) + self.step) % len(family)]
        return reverse('cards:revision', kwargs={'slug': new_card.slug, 'dsp_card_on_load': True})


class RevisionPreviousCardView(RevisionPermissionMixin, RevisionNextCardView):
    step = -1


class RevisionView(RevisionPermissionMixin, DetailView):
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
            card__in=card.family(self.request.user),
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
        context.update(other_versions=len(self.object.card.family(self.request.user)) > 1)
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


class RevisionStats(RevisionPermissionMixin, TemplateView):
    template_name = 'cards/stats.html'

    def get_context_data(self, *args, **kwargs):
        data = DataPool(
            series=[
                {'options': {
                    'source': self.request.user.deck.all()},
                    'terms': [
                        'modified',
                        'nb_views']}
            ]
        )
        #  Step 2: Create the Chart object
        cht = Chart(
            datasource=data,
            series_options=[
                {'options':{
                    'type': 'line',
                    'stacking': False},
                    'terms':{
                        'modified': [
                            'nb_views',
                        ]
                    }}],
            chart_options=
            {'title': {
                'text': 'Weather Data of Boston and Houston'},
                'xAxis': {
                    'title': {
                        'text': 'Month number'}}}
        )

        #Step 3: Send the chart object to the template.
        return super().get_context_data(cards_chart=cht)


class ListCardView(RevisionPermissionMixin, ListView):
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
