from django.core.management.base import BaseCommand
from oscar.core.loading import get_class, get_classes

from sklearn.externals import joblib
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import SGDClassifier


Classifier, Question, Prediction, Speciality = get_classes('confs.models', ("Classifier", "Question", "Prediction", "Speciality"))


def classifier(text_clf, string):
    prediction = text_clf.predict_proba([string])
    classement = sorted(zip(prediction[0], text_clf.classes_), reverse = True)
    return [i[1] for i in classement[:3]]


class Command(BaseCommand):
    help = 'Update all classifier predictions for all questions in the "Prediction" table'

    def handle(self, *args, **options):
        cl = Classifier.objects.get(name="toto")
        text_clf = joblib.load(cl.classifier)
        for interrogation in Question.objects.all():
            pred, _ = Prediction.objects.get_or_create(question = interrogation, classifier = cl)
            for p in classifier(text_clf, (interrogation.conf.statement or "")+" "+(interrogation.question or "")+" "+(interrogation.explaination or "")):
                if not (p == "Hématologie - Oncohématologie" or p == "Pharmacologie"):
                    pred.specialities.add(Speciality.objects.get(name=p))
            pred.save()
