import re
import logging
import random
from datetime import timedelta, datetime, MINYEAR
from django.utils import timezone
from django.core.urlresolvers import reverse_lazy
import pytz

from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.db.models import Q, Count, Min
from django.http import JsonResponse
from django.views.generic import (
    ListView,
    UpdateView,
    CreateView,
    DetailView,
    RedirectView,
    TemplateView,
    FormView,
)
from jchart import Chart
from jchart.config import DataSet
from blousebrothers.auth import BBLoginRequiredMixin
from blousebrothers.confs.models import Item, Speciality
from blousebrothers.users.models import User
from .revision_steps import revision_steps
from .models import Card, Deck, Session, CardsPreference, SessionOverException
from .forms import CreateCardForm, UpdateCardForm, FinalizeCardForm, AnkiFileForm
from .loader import load_apkg

logger = logging.getLogger(__name__)


def create_new_session(request, specialities, items, revision):
    """
    Create new revision session record
    """
    Session.objects.filter(student=request.user).update(finished=True)
    try:
        duration = request.user.cards_preference.get().session_duration
    except:
        duration = CardsPreference.objects.get_or_create(student=request.user)[0].session_duration
    session = Session.objects.create(student=request.user, selected_duration=duration, revision=revision)
    session.specialities = specialities
    session.items = items
    session.save()
    return session


def get_or_create_session(request):
    """
    Get current session or create new session
    """
    specialities = Speciality.objects.filter(pk__in=[request.GET.get('specialities')] or [])
    items = Item.objects.filter(pk__in=request.GET.get('items') or [])
    revision = request.GET.get('revision') == 'True'

    session = Session.objects.filter(student=request.user, finished=False).first()
    if not session:
        session = create_new_session(request, specialities, items, revision)
    else:
        session.check_is_not_over()
    return session


def get_session(request):
    return Session.objects.filter(student=request.user, finished=False).first()


def choose_new_card(request):
    """
    Hot point. All requests for new card are done here.
    """
    session = get_or_create_session(request)
    if session.revision:
        new_card = session.choose_revision_card()
    else:
        # choose a new original card never done by user
        new_card = session.new_cards.first()
        # if all card are already done choose revision card
        if not new_card:
            new_card = random.choice(session.matching_cards.all()[:20])

    session.cards.add(new_card)
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


class RevisionPermissionMixin(UserPassesTestMixin):

    def test_func(self):
        self.object = self.get_object()
        if isinstance(self.object, Card):
            card = self.object
        else:
            card = self.object.card
        if not self.request.user.is_authenticated():
            return card.public
        else:
            return card.author is None or card.author == self.request.user or card.public \
                or card.author.id in self.request.user.to_people.filter(
                    share_cards=True).values_list('from_user_id', flat=True)

    def handle_no_permission(self):
        if not self.request.user.is_authenticated():
            return BBLoginRequiredMixin.handle_no_permission(self)
        raise PermissionDenied


class CreateCardView(BBLoginRequiredMixin, CreateView):
    model = Card
    form_class = CreateCardForm

    def get_success_url(self):
        return reverse('cards:finalize', kwargs={'pk': self.object.id})

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


class Mock:
    card = None


class MockDeckMixin():
    """
    Share same template as Revision view. Because Revision view use Deck
    as model, we mock Deck model with another class.
    """

    def get_context_data(self, **kwargs):
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

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return redirect(reverse('account_login'))
        else:
            return super().get(request, *args, **kwargs)

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
        return reverse('cards:revision', kwargs={'id': self.object.id})


class RevisionCloseSessionView(BBLoginRequiredMixin, RedirectView):
    url = reverse_lazy('cards:home')

    def get(self, request, *args, **kwargs):
        session = get_session(self.request)
        if session:
            #  remove last card, because no click on easy/medium...
            if kwargs["id"] != "sessionover":
                session.cards.remove(Card.objects.get(id=kwargs["id"]))
            session.effective_duration = timezone.now() - session.date_created
            session.finished = True
            session.save()
            duration = session.effective_duration.seconds // 60
            duration_msg = " en {} minute{}".format(duration, "s" if duration > 1 else "") if duration else ""

            if session.cards.count():
                messages.info(self.request,
                              "Tu as {} {} fiches{}.".format(
                                  "révisé" if session.revision else "vu",
                                  session.cards.count(),
                                  duration_msg,
                              )
                              )
        return super().get(request, *args, **kwargs)


class RevisionDeleteView(BBLoginRequiredMixin, DetailView):
    model = Deck
    success_url = reverse_lazy('cards:redirect')

    def get(self, *args, **kwargs):
        self.object = self.get_object()
        self.object.trashed = True
        self.object.save()
        return redirect('cards:redirect')


class RevisionRedirectView(BBLoginRequiredMixin, RedirectView):
    """
    Root url of card app, reached by clicking on revision or learn links.
    Choose a card and redirect to revision view.
    """

    def get_redirect_url(self, *args, **kwargs):
        try:
            new_card = choose_new_card(self.request)
            return reverse('cards:revision', kwargs={'id': new_card.id})
        except SessionOverException:
            return reverse('cards:stop', kwargs={'id': 'sessionover'})


class RevisionNextCardView(BBLoginRequiredMixin, RedirectView):
    """
    Called when clicking on next card button.
    """
    step = 1

    def get_redirect_url(self, *args, **kwargs):
        current_card = Card.objects.get(pk=args[0])
        family = current_card.family(self.request.user)
        new_card = family[(family.index(current_card) + self.step) % len(family)]
        return reverse('cards:revision', kwargs={'id': new_card.id, 'dsp_card_on_load': True})


class RevisionPreviousCardView(RevisionNextCardView):
    step = -1


class RevisionView(RevisionPermissionMixin, DetailView):
    """
    Zen card view for revision.
    """
    template_name = "cards/revision.html"
    model = Deck
    is_favorite = False

    def get_object(self, queryset=None):
        """
        Only one card by family in user's deck. If a sibling card is present
        in user's deck, we return this deck instance with the requested card.
        Otherwise we create a new desk instance with request card.
        """
        card = Card.objects.get(id=self.kwargs['id'])

        if not self.request.user.is_authenticated():
            obj = Mock()
            obj.card = card
            return obj

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
        if self.request.user.is_authenticated():
            context.update(other_versions=len(self.object.card.family(self.request.user)) > 1)
        context.update(zen=True)
        return context

    def update_deck(self, difficulty):
        delta = revision_steps[self.object.column].next_time[difficulty]
        if (delta < timedelta(days=1)):
            self.object.wake_up = timezone.now()+delta
        else:
            self.object.wake_up = timezone.now()+delta
            self.object.wake_up.replace(hour=5)
        self.object.column = revision_steps[self.object.column].get_next_column(difficulty).column
        self.object.difficulty = difficulty
        self.object.save()

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return redirect(reverse('account_login'))
        self.object = self.get_object()
        if 'easy' in request.POST:
            self.update_deck(0)
        elif 'average' in request.POST:
            self.update_deck(1)
        elif 'hard' in request.POST:
            self.update_deck(2)
        try:
            new_card = choose_new_card(request)
            return redirect(reverse('cards:revision', kwargs={'id': new_card.id}))
        except SessionOverException:
            return redirect(reverse('cards:stop', kwargs={'id': 'sessionover'}))


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

    def get_labels(self, *args, **kwargs):
        return [str(Deck.DIFFICULTY_CHOICES[label[0]]) for label in Deck.DIFFICULTY_CHOICES]

    def get_lab_col_cnt(self):
        """
        Used in template to display stat in table
        """
        return zip(self.get_labels(), self.colors, self.data)

    def get_datasets(self, spe, **kwargs):
        user = self.request.user
        if user.is_anonymous():
            user = User.objects.get(username='BlouseBrothers')

        qs = Deck.objects.filter(student=user)
        if spe:
            qs = qs.filter(card__specialities__id__exact=spe.id)
        dom = qs.values('difficulty').annotate(nb_dif=Count('difficulty'))
        self.data = [next((l['nb_dif'] for l in dom if l['difficulty'] == i), 0) for i in range(3)]
        return [DataSet(data=self.data,
                        label="Répartition des fiches",
                        backgroundColor=self.colors,
                        hoverBackgroundColor=self.colors)]


class RevisionHome(TemplateView):
    template_name = 'cards/home.html'

    def get_context_data(self, *args, **kwargs):
        user = self.request.user
        if user.is_anonymous():
            user = User.objects.get(username='BlouseBrothers')
        dispatching_chart = Dispatching()
        dispatching_chart.request = self.request
        total_count = Card.objects.for_user(user).values('specialities').annotate(
            spe_count=Count('specialities')
        )
        user_count = user.deck.values('card__specialities').annotate(
            spe_count=Count('card__specialities'),
            wake_up=Min('wake_up')
        )
        ready_count = user.deck.values('card__specialities').filter(wake_up__lt=timezone.now()).annotate(
            spe_count=Count('card__specialities')
        )
        mindate = datetime(MINYEAR, 1, 1, tzinfo=pytz.UTC)
        specialities = [
            {'obj': spe,
             'total': next((l['spe_count'] for l in total_count if l['specialities'] == spe.id), 0),
             'user': next((l['spe_count'] for l in user_count if l['card__specialities'] == spe.id), 0),
             'ready': next((l['spe_count'] for l in ready_count if l['card__specialities'] == spe.id), 0),
             'wake_up': next((l['wake_up'] for l in user_count if l['card__specialities'] == spe.id), 0),
             'last_access': next((l['wake_up'] for l in user_count if l['card__specialities'] == spe.id), 0),
             }
            for spe in Speciality.objects.all()
        ]
        specialities.sort(key=lambda x: x['total'], reverse=True)
        specialities.sort(key=lambda x: x['last_access'] if x['last_access'] else mindate, reverse=True)
        return super().get_context_data(
            *args,
            retro_img_nb=random.randint(1, 13),
            chart=dispatching_chart,
            specialities=specialities,
            wake_up=min((l['wake_up'] for l in user_count)) if user_count else 0,
            ready=sum((l['spe_count'] for l in ready_count)),
            total=Card.objects.for_user(user).count(),
            anki_form=AnkiFileForm(),
            **kwargs
        )


class ListCardView(BBLoginRequiredMixin, ListView):
    model = Deck
    paginate_by = 50
    trashed = False

    def get_queryset(self):
        qry = self.model.objects.filter(student=self.request.user, trashed=self.trashed)
        qry = qry.prefetch_related('card')
        if self.request.GET.get('q', False):
            qry = qry.filter(
                Q(card__content__icontains=self.request.GET['q']) |
                Q(card__tags__name__icontains=self.request.GET['q'])
            )
        return qry.all().order_by('-created')


class ListTrashedCardView(ListCardView):
    model = Deck
    paginate_by = 50
    template_name = 'cards/trash_list.html'
    trashed = True


class AnkiUploadView(BBLoginRequiredMixin, FormView):
    form_class = AnkiFileForm
    template_name = 'cards/anki.html'
    success_url = reverse_lazy('cards:home')

    def form_valid(self, form):
        try:
            load_apkg(form.cleaned_data["ankifile"], self.request.user)
            messages.info(self.request,
                          "Le fichier a bien été reçu. Les fiches devraient être disponibles "
                          "d'ici quelques minutes (2 minutes pour une archive de 30 Mo...)"
                          )
        except:
            logger.exception("Anki import failed")
            messages.error(self.request, "Un problème est survenu lors de l'import du fichier :/")
            return super().form_valid(form)
