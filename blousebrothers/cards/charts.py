from django.db.models import Count
from jchart import Chart
from jchart.config import DataSet

from blousebrothers.users.models import User
from .models import Deck


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
