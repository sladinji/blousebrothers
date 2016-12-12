
from django.db import migrations


def create_answersimages(apps, schema_editor):
    Answer = apps.get_model('confs', 'Answer')
    AnswerImage = apps.get_model('confs', 'AnswerImage')
    for answer in Answer.objects.exclude(explaination_image='').all():
        AnswerImage.objects.create(image=answer.explaination_image,
                                   cropping=answer.cropping,
                                   answer=answer,
                                   )


class Migration(migrations.Migration):

    dependencies = [
        ('confs', '0027_auto_20161209_1619'),
    ]

    operations = [
        # omit reverse_code=... if you don't want the migration to be reversible.
        migrations.RunPython(create_answersimages),
    ]
