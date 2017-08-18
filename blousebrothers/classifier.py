from blousebrothers.confs.models import Classifier

from sklearn.externals import joblib
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import SGDClassifier

__classifier = None


def classifier(string):
    global __classifier
    if not __classifier:
        __classifier = joblib.load(Classifier.objects.first().classifier)
    prediction = __classifier.predict_proba([string])
    classement = sorted(zip(prediction[0], __classifier.classes_), reverse = True)
    return [i[1] for i in classement[:3]]
