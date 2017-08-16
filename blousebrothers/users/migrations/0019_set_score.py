import ast
from decimal import Decimal
from django.db import migrations, models


def set_score(apps, schema_editor):
    Test = apps.get_model('confs', 'Test')
    try:
        for test in Test.objects.filter(finished=True).all():
            for ta in test.answers.all():
                ta.max_point = ta.question.coefficient
                ga = ast.literal_eval(ta.given_answers + ',')
                omissions = [ans for ans in ta.question.answers.filter(correct=True)
 if ans.index not in ga]
                errors = [ans for ans in ta.question.answers.filter(correct=False)
 if ans.index in ga]
                bga = omissions + errors
                ta.nb_errors = len(bga)
                fatals = [x for x in bga if x.ziw]
                if fatals:
                    ta.fatals.add(*fatals)
                if sorted(ga) == sorted([x.index for x in ta.question.answers.filter(correct=True)
]):
                    ta.point = ta.max_point
                elif len(bga) > 2 or fatals:
                    ta.point = 0
                elif len(bga) == 2:
                    ta.point = Decimal(0.2 * ta.question.coefficient)
                elif len(bga) == 1:
                    ta.point = Decimal(0.5 * ta.question.coefficient)
                ta.save()
            test.max_point = test.answers.aggregate(models.Sum('max_point')).get("max_point__sum")
            test.point = test.answers.aggregate(models.Sum('point')).get("point__sum")
            test.score = test.point / test.max_point * 100
            test.save()

    except Exception as ex:
        print(ex)


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0018_merge'),
    ]

    operations = [
        # omit reverse_code=... if you don't want the migration to be reversible.
        migrations.RunPython(set_score, reverse_code=lambda x, y : True),
    ]
