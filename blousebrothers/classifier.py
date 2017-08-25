import logging

from sklearn.externals import joblib

from blousebrothers.confs.models import Classifier

__classifier = None

logger = logging.getLogger(__name__)


def classifier(string):
    global __classifier
    try:
        if not __classifier:
            __classifier = joblib.load(Classifier.objects.first().classifier)
    except:
        logger.exception("No classifier available")
        return []
    prediction = __classifier.predict_proba([string])
    classement = sorted(zip(prediction[0], __classifier.classes_), reverse=True)
    return [i[1] for i in classement[:3]]
