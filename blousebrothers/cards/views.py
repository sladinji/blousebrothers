import re

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
from jchart import Chart
from jchart.config import DataSet

from blousebrothers.auth import BBLoginRequiredMixin
from blousebrothers.confs.models import Item
from blousebrothers.users.models import User
from .models import Card, Deck
from .forms import CreateCardForm, UpdateCardForm, FinalizeCardForm


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
        return reverse('cards:finalize', kwargs={'slug': self.object.slug})

    def form_valid(self, form):
        """
        Find items and spe for the given data, and add @@ makers.
        """
        txt = "{question} {content}".format(**form.cleaned_data)
        self.object = form.save()

        for item in Item.objects.all():
            for kw in item.kwords.all():
                if re.search(r'[^\w]'+kw.value+r'([^\w]|$)', txt):
                    self.object.items.add(item)
                    break

        self.object.content = '@@{question}@@\n{content}'.format(**form.cleaned_data)
        self.object.author = self.request.user
        self.object.save()

        Deck.objects.create(card=self.object, student=self.request.user)

        return super().form_valid(form)


class MockDeckMixin():
    """
    Share same template as Revision view. Because Revision view use Deck
    as model, we mock Deck model with another class.
    """

    def get_context_data(self, **kwargs):
        class Mock:
            card = None

        context = super().get_context_data(**kwargs)
        mock = Mock()
        mock.card = context['object']
        context.update(object=mock)
        return context


class FinalizeCardView(MockDeckMixin, RevisionPermissionMixin, UpdateView):
    model = Card
    form_class = FinalizeCardForm

    def get_success_url(self):
        return reverse('cards:list')


class UpdateCardView(MockDeckMixin, RevisionPermissionMixin, UpdateView):
    model = Card
    form_class = UpdateCardForm

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
        context.update(zen=True)
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


class Dispatching(Chart):
    """
    How many cards in each category.
    """
    chart_type = 'doughnut'
    request = None
    responsive = True
    maintainAspectRatio = False
    legend = {
        'display': False,
        'position': 'right',
    }
    colors = [
        "#5cb85c",
        "#E8B510",
        "#d9534f"
    ]

    def get_labels(self, **kwargs):
        return [str(label[1]) for label in Card.LEVEL_CHOICES]

    def get_lab_col_cnt(self):
        """
        Used in template to display stat in table
        """
        return zip(self.get_labels(), self.colors, self.data)

    def get_datasets(self, **kwargs):
        user = self.request.user
        if user.is_anonymous():
            user = User.objects.get(username='BlouseBrothers')

        self.data = [Deck.objects.filter(student=user, difficulty=dif).count()
                     for dif in range(3)]
        return [DataSet(data=self.data,
                        label="Répartition des fiches",
                        backgroundColor=self.colors,
                        hoverBackgroundColor=self.colors)]


class RevisionHome(TemplateView):
    template_name = 'cards/home.html'

    def get_context_data(self, *args, **kwargs):
        dispatching_chart = Dispatching()
        dispatching_chart.request = self.request
        return super().get_context_data(*args, chart=dispatching_chart, **kwargs)


class ListCardView(ListView):
    model = Card

    def get_queryset(self):
        if self.request.user.is_anonymous():
            qry = self.model.objects.filter(public=True)
        else:
            qry = self.model.objects.filter(deck__student=self.request.user)
            if self.request.GET.get('q', False):
                qry = qry.filter(
                    Q(content__icontains=self.request.GET['q']) |
                    Q(tags__name__icontains=self.request.GET['q'])
                )
        return qry.all().order_by('-deck__created')
