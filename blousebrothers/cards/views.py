import re
import logging
import random
from decimal import Decimal
from decimal import ROUND_DOWN
from datetime import timedelta, datetime, MINYEAR
from django.utils import timezone
from django.core.urlresolvers import reverse_lazy
import pytz

from django.db.models import Sum
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, get_object_or_404
from django.db.models import Q, Count, Min
from django.http import JsonResponse
from django.apps import apps
from django.views.generic import (
    ListView,
    UpdateView,
    CreateView,
    DetailView,
    RedirectView,
    TemplateView,
    FormView,
)
from blousebrothers.auth import BBLoginRequiredMixin
from blousebrothers.confs.models import Item, Speciality, Conference
from blousebrothers.users.models import User
from .revision_steps import revision_steps
from .models import Card, Deck, Session, CardsPreference, SessionOverException, CardImage, Tag
from .forms import CreateCardForm, UpdateCardForm, FinalizeCardForm, AnkiFileForm, CardHomeAdvancedFilterForm
from .loader import anki, text
from .charts import Dispatching
from blousebrothers.confs.templatetags.bbtricks import HT


logger = logging.getLogger(__name__)
Order = apps.get_model('order', 'Order')


def create_new_session(request, specialities, items, revision, tags, search):
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
    session.tags = tags
    session.search = search
    session.save()
    return session


def get_or_create_session(request):
    """
    Get current session or create new session
    """
    specialities = Speciality.objects.filter(pk__in=[request.GET.get('specialities')] or [])
    items = Item.objects.filter(pk__in=request.GET.get('items') or [])
    tags = Tag.objects.filter(pk__in=request.GET.get('tags') or [])
    revision = request.GET.get('revision') == 'True'
    search = request.GET.get('search', '')

    session = Session.objects.filter(student=request.user, finished=False).first()
    if not session:
        session = create_new_session(request, specialities, items, revision, tags, search)
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
            new_card = random.choice(session.matching_cards().all()[:20])

    session.cards.add(new_card)
    return new_card


def bookmark_card(request, card_id):
    """
    Ajax view.
    Bookmark given card by updating user deck with given card.
    Other revision of the card are parent or brothers of the given card.
    """
    if request.user.is_anonymous():
        return HttpResponse(status=410)

    bcard = Card.objects.get(pk=card_id)
    Deck.objects.filter(
        Q(card__in=bcard.children.all()) | Q(card=bcard.parent),
        student=request.user
    ).update(card=bcard)
    return JsonResponse({'success': True})


class RevisionPermissionMixin(UserPassesTestMixin):

    def test_func(self):
        """
        Check if trial period is over and if user is allowed to access requested object.
        """
        #  Check Trial Period
        if self.request.user.is_authenticated and self.request.user.deck.count() > 50:
            try:
                if not self.request.user.subscription.type.product.attr.access_cards:
                    return False
            except:
                return False

        #  Check if user is authenticated to access ListView (UnseenCardsListView, ListTrashedCardView ...)
        if not hasattr(self, 'get_object'):
            if self.request.user.is_authenticated:
                return True
            else:
                return False

        # Check if user can access requested object (RevisionView, RevisionNextCardView...)
        self.object = self.get_object()
        if isinstance(self.object, Card):
            card = self.object
        else:
            card = self.object.card
        if not self.request.user.is_authenticated:
            return card.public
        else:
            return Card.objects.for_user(self.request.user).filter(id=card.id).exists() or \
                self.request.user.deck.filter(card=card).exists()

    def handle_no_permission(self):
        """
        Ask user to login or to subscribe to a cards plan.
        """
        if not self.request.user.is_authenticated:
            return BBLoginRequiredMixin.handle_no_permission(self)
        try:
            if not self.student.subscription.type.product.attr.access_cards:
                return redirect(reverse('cards:stop', kwargs={'id': 'trialover'}))
        except:
            return redirect(reverse('cards:stop', kwargs={'id': 'trialover'}))
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
        image = form.cleaned_data['image']
        if image:
            cimage = CardImage(owner=self.request.user, image=image)
            cimage.save()
            self.object.content += '<br><img src="{}"/>'.format(cimage.image.url)
        self.object.save()

        Deck.objects.create(card=self.object, student=self.request.user)

        return super().form_valid(form)


class Mock:
    card = None

    def __init__(self, card=None):
        self.card = card


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
        if not request.user.is_authenticated:
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
        if kwargs["id"] == "trialover":
            messages.info(self.request, "Tu es arrivé au bout de la période d'essai du module de révision. "
                          "Si l'outil te plait et que tu souhaites continuer, merci de souscrire à un abonnement."
                          )
            return redirect('users:redirect')

        session = get_session(self.request)
        if session:
            #  remove last card, because no click on easy/medium...
            if kwargs["id"] not in ("sessionover", "trialover"):
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


class StartRevisionSession(RevisionRedirectView):
    """
    Close user's sessions before calling RevisionRedirectView.
    """

    def get_redirect_url(self, *args, **kwargs):
        Session.objects.filter(student=self.request.user).update(finished=True)
        return super().get_redirect_url(*args, **kwargs)


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
        Permission check is done on card. So we just return the card. Object is supposed to
        be a Deck instance, but we have to check user's permission on card before : if user's
        doesn't have permission anymore with requested card but the card is already in his deck,
        he still can access to it. This means we have to get or create deck instance later
        because we first have to check if record already exists !
        """
        return get_object_or_404(Card, pk=self.kwargs['id'])

    def get(self, request, *args, **kwargs):
        card = self.get_object()

        if not self.request.user.is_authenticated:
            obj = Mock()
            obj.card = card
        else:
            obj = Deck.objects.get_or_create(card=card, student=self.request.user)[0]
            self.is_favorite = True

        context = self.get_context_data(object=obj)
        return self.render_to_response(context)

    def get_context_data(self, *args, **kwargs):
        context = {}
        context.update(is_favorite=self.is_favorite, **kwargs)
        context.update(dsp_card_on_load=self.kwargs['dsp_card_on_load'] == "True")
        if self.request.user.is_authenticated:
            context.update(other_versions=len(context['object'].card.family(self.request.user)) > 1)
        context.update(zen=True)
        return context

    def update_deck(self, difficulty):
        deck = self.request.user.deck.get(card_id=self.kwargs['id'])
        delta = revision_steps[deck.column].next_time[difficulty]
        if (delta < timedelta(days=1)):
            deck.wake_up = timezone.now()+delta
        else:
            deck.wake_up = timezone.now()+delta
            deck.wake_up.replace(hour=5)
        deck.column = revision_steps[deck.column].get_next_column(difficulty).column
        deck.difficulty = difficulty
        deck.save()

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
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


class RevisionHome(TemplateView):
    template_name = 'cards/home.html'

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        user = self.request.user
        qry = Card.objects.for_user(user)
        if user.is_authenticated:
            deck = user.deck
            ctx.update(**user.stats)
        else:
            deck = User.objects.get(username="BlouseBrothers").deck
        for filters in ['specialities', 'items', 'tags']:
            ids = self.request.GET.getlist(filters)
            if ids:
                qry = qry.filter(**{filters+'__id__in': ids})
                deck = deck.filter(**{'card__'+filters+'__id__in': ids})
        search = self.request.GET.get('search', '')
        if search:
            qry = qry.filter(
                Q(content__icontains=search) |
                Q(specialities__name__icontains=search) |
                Q(tags__name__icontains=search) |
                Q(items__name__icontains=search)
            )
            deck = deck.filter(
                Q(card__content__icontains=search) |
                Q(card__specialities__name__icontains=search) |
                Q(card__tags__name__icontains=search) |
                Q(card__items__name__icontains=search)
            )
        if user.is_anonymous():
            user = User.objects.get(username='BlouseBrothers')
        dispatching_chart = Dispatching()
        dispatching_chart.request = self.request
        total_count = qry.values('specialities').annotate(
            spe_count=Count('specialities')
        )
        user_count = deck.values('card__specialities').annotate(
            spe_count=Count('card__specialities'),
            wake_up=Min('wake_up')
        )
        ready_count = deck.values('card__specialities').filter(wake_up__lt=timezone.now()).annotate(
            spe_count=Count('card__specialities')
        )
        mindate = datetime(MINYEAR, 1, 1, tzinfo=pytz.UTC)
        spe_qry = Speciality.objects.all()
        spe_ids = self.request.GET.getlist('specialities')
        if spe_ids:
            spe_qry = spe_qry.filter(id__in=spe_ids)
        specialities = [
            {'obj': spe,
             'total': next((l['spe_count'] for l in total_count if l['specialities'] == spe.id), 0),
             'user': next((l['spe_count'] for l in user_count if l['card__specialities'] == spe.id), 0),
             'ready': next((l['spe_count'] for l in ready_count if l['card__specialities'] == spe.id), 0),
             'wake_up': next((l['wake_up'] for l in user_count if l['card__specialities'] == spe.id), 0),
             'last_access': next((l['wake_up'] for l in user_count if l['card__specialities'] == spe.id), 0),
             }
            for spe in spe_qry.all()
        ]
        specialities.sort(key=lambda x: x['total'], reverse=True)
        specialities.sort(key=lambda x: x['last_access'] if x['last_access'] else mindate, reverse=True)
        ctx.update(
            retro_img_nb=random.randint(1, 13),
            chart=dispatching_chart,
            specialities=specialities,
            wake_up=min((l['wake_up'] for l in user_count)) if user_count else 0,
            ready=sum((l['spe_count'] for l in ready_count)),
            total=qry.count(),
            form=CardHomeAdvancedFilterForm(
                initial={
                    'items': self.request.GET.getlist('items'),
                    'specialities': self.request.GET.getlist('specialities'),
                    'tags': self.request.GET.getlist('tags'),
                }
            ),
            deck=deck,
            filter_visible=self.request.GET.getlist(
                'items'
            ) or self.request.GET.getlist(
                'specialities'
            ) or self.request.GET.getlist(
                'tags'
            ),
            last_confs=Conference.objects.exclude(
                deleted=True,
            ).filter(
                products__isnull=False,
                for_sale=True,
            ).order_by('-date_created')[:4]
        )
        return ctx


class RevisionGroups(RevisionHome):
    template_name = 'cards/revision_groups.html'


class ListCardView(RevisionPermissionMixin, ListView):
    model = Deck
    paginate_by = 25
    trashed = False

    def get_queryset(self):
        qry = self.model.objects.filter(student=self.request.user, trashed=self.trashed)
        qry = qry.prefetch_related('card')
        if self.request.GET.get('search', False):
            and_list = []
            for element in self.request.GET['search'].split():
                and_list.append(Q(card__content__icontains=element))
            sub_qry = and_list.pop()
            for q in and_list:
                sub_qry &= q
            qry = qry.filter(sub_qry | Q(card__tags__name__icontains=self.request.GET['search']))
        for filters in ['specialities', 'items', 'tags']:
            ids = self.request.GET.getlist(filters)
            if ids:
                qry = qry.filter(**{'card__' + filters + '__id__in': ids})
        return qry.all().order_by('-created')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(
            form=CardHomeAdvancedFilterForm(
                initial={
                    'items': self.request.GET.getlist('items'),
                    'specialities': self.request.GET.getlist('specialities'),
                    'tags': self.request.GET.getlist('tags'),
                }
            ),
            filter_visible=self.request.GET.getlist(
                'items'
            ) or self.request.GET.getlist(
                'specialities'
            ) or self.request.GET.getlist(
                'tags'
            ),
        )
        return ctx


class ListTrashedCardView(ListCardView):
    model = Deck
    paginate_by = 25
    template_name = 'cards/trash_list.html'
    trashed = True


class UnseenCardsListView(ListCardView):
    paginate_by = 25
    template_name = 'cards/unseen_cards_list.html'
    trashed = True

    def get_queryset(self, studentsearch=None):
        return Card.new_cards(
            self.request.user,
            search=self.request.GET.get('search', None),
            items=self.request.GET.getlist('items'),
            specialities=self.request.GET.getlist('specialities'),
            tags=self.request.GET.getlist('tags'),
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(object_list=[Mock(x) for x in ctx['object_list']])
        return ctx


class AnkiUploadView(BBLoginRequiredMixin, FormView):
    form_class = AnkiFileForm
    template_name = 'cards/anki.html'
    success_url = reverse_lazy('cards:home')

    def form_valid(self, form):
        try:
            if form.cleaned_data["ankifile"].name.endswith("txt"):
                text.load(form.cleaned_data["ankifile"], self.request.user)
                messages.info(self.request,
                              "Fichier importé !"
                              )
            else:
                anki.load_apkg(form.cleaned_data["ankifile"], self.request.user)
                messages.info(self.request,
                              "Le fichier a bien été reçu. Les fiches devraient être disponibles "
                              "d'ici quelques minutes (2 minutes pour une archive de 30 Mo...)"
                              )
        except:
            logger.exception("Anki import failed")
            messages.error(self.request, "Un problème est survenu lors de l'import du fichier :/")
        return super().form_valid(form)


class BouletListView(UserPassesTestMixin, ListView):
    model = Order
    # These next two lines tell the view to index lookups by conf
    paginate_by = 20
    template_name = 'cards/boulet.html'

    def test_func(self):
        return self.request.user.username == 'Nicota' or self.request.user.is_superuser

    def handle_no_permission(self):
        raise PermissionDenied()

    def get_queryset(self):
        qry = Order.objects.filter(
            lines__product__attribute_values__attribute__name='access_cards',
            lines__product__attribute_values__value_boolean=True,
        )
        return qry.all()

    def get_context_data(self, **kwargs):
        double = Order.objects.filter(
            lines__product__attribute_values__attribute__name='access_cards',
            lines__product__attribute_values__value_boolean=True,
        )
        double = double.filter(
            lines__product__attribute_values__attribute__name='access_confs',
            lines__product__attribute_values__value_boolean=True,
        )
        simple = Order.objects.filter(
            lines__product__attribute_values__attribute__name='access_cards',
            lines__product__attribute_values__value_boolean=True,
        )
        simple = simple.filter(
            lines__product__attribute_values__attribute__name='access_confs',
            lines__product__attribute_values__value_boolean=False,
        )

        total_simple = HT(simple.aggregate(total_simple=Sum('total_incl_tax'))['total_simple'])
        total_double = HT(double.aggregate(total_double=Sum('total_incl_tax'))['total_double'])
        total_simple_du = (total_simple / Decimal(2)).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
        total_double_du = (total_double / Decimal(4)).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
        total_du = total_simple_du + total_double_du
        return super().get_context_data(
            total_simple=total_simple,
            total_simple_du=total_simple_du,
            total_double=total_double,
            total_double_du=total_double_du,
            total_du=total_du
        )
