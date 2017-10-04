from datetime import date
import numpy as np

from jchart import Chart
from jchart.config import Axes, DataSet, rgba

from .models import User
from blousebrothers.confs.models import StatsSpe


class MeanBarChart(Chart):
    chart_type = 'bar'
    scales = {
        'yAxes': [
            Axes(ticks={
                'beginAtZero': True,
                "max": 100},
                gridLines={
                    'display': False,
                }
            )
        ],
        'xAxes': [
            Axes(ticks={
                'display': False,
            }
            )
        ]
    }
    context = None

    def color_picker(self, nb_categories):
        scale = np.linspace(0.0, 5.0, num=nb_categories, endpoint=True)
        color_scale = []
        for i in scale:
            if 0 <= i < 1:
                r = 255
                g = 0
                b = (1-i)*255
            elif 1 <= i < 2:
                r = 255
                g = (i-1)*255
                b = 0
            elif 2 <= i < 3:
                r = (3-i)*255
                g = 255
                b = 0
            elif 3 <= i < 4:
                r = 0
                g = 255
                b = (i-3)*255
            else:
                r = 0
                g = (5-i)*255
                b = 255
            color_scale.append(rgba(int(r), int(g), int(b), 0.4))
        return color_scale

    def get_labels(self, **kwargs):
        labels_spe = [spe[0] for spe in self.user_stats]
        return labels_spe

    def get_user_stats(self, user_id):
        user = User.objects.get(pk=user_id)
        notes_spe = {}
        for test in user.tests.filter(finished=True).prefetch_related('conf__specialities'):
            for spe in test.conf.specialities.all():
                if spe.name in notes_spe:
                    notes_spe[spe.name].append(test.score)
                else:
                    notes_spe[spe.name] = [test.score]
        return sorted(
            [(spe, round(np.mean(notes_spe[spe]), 2)) for spe in notes_spe],
            key=lambda x: x[1],
            reverse=False
        ), user

    def get_datasets(self, **kwargs):
        self.user_stats = self.get_user_stats(kwargs["user_id"])[0]
        if kwargs['friend_id'] == '0':
            stats = dict(StatsSpe.objects.values_list('speciality__name', 'average'))
            other_stats = []
            for spe, _ in self.user_stats:
                other_stats.append(stats[spe])
                other_label = "Moyenne de tous les utilisateurs"
        else:
            other_raw_stats, friend = self.get_user_stats(kwargs["friend_id"])
            dic_other_stat = dict(other_raw_stats)
            other_stats = [dic_other_stat.get(spe[0], 0) for spe in self.user_stats]
            other_label = friend.username
        colors = self.color_picker(len(self.user_stats))
        return [DataSet(label='Ma moyenne',
                        data=[spe[1] for spe in self.user_stats],
                        backgroundColor=colors),
                DataSet(label=other_label,
                        data=other_stats,
                        type='line')]


class MonthlyLineChart(Chart):
    chart_type = 'line'
    scales = {
        "yAxes": [
            Axes(ticks={
                "beginAtZero": True,
                "suggestedMax": 10,
            },
                gridLines={
                    'display': False,
                }
            )
        ]
    }
    context = None
    d = {}

    def get_labels(self, **kwargs):
        year = date.today().year
        return ["Juillet {}".format(year), "Août", "Septembre", "Octobre", "Novembre", "Décembre",
                "Janvier {}".format(year + 1), "Février", "Mars", "Avril", "Mai", "Juin"]

    def get_datasets(self, **kwargs):
        year = date.today().year
        self.d = {i: 0 for i in range(1, 13)}
        user = User.objects.get(pk=self.context['object'].pk)
        for x in user.tests.filter(finished=True, date_created__range=(date(year, 7, 1), date(year+1, 7, 1))):
            self.d[x.date_created.month] += 1
        data = sorted([(mois, self.d[mois]) for mois in self.d])
        return [DataSet(label='Dossiers terminés',
                data=[nb[1] for nb in data[7:]+data[:7]])]
