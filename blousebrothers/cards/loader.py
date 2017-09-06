import difflib
import zipfile
import tempfile
import sqlite3
import os
import logging
from blousebrothers.confs.models import Speciality
from blousebrothers.cards.models import Card

logger = logging.getLogger(__name__)

rep_map = {
    "ologie": "",
    "icono": "",
    "é": "e",
    "è": "e",
    "à": "a",
    "ç": "c",
    "î": "i",
    "ê": "e",
    "â": "a",
    "ô": "o",
}


def clean(word):
    word = word.strip()
    word = word.lower()
    for k, v in rep_map.items():
        word = word.replace(k, v)
    return word

# Dictionnary of spe by word to enhance matches
spe_dic = {
    clean(word): spe
    for spe in Speciality.objects.all()
    for word in spe.other_names.split(",")
}


def get_specialities(spelist):
    """
    Get close match (remove "ologie" from str for better perfromances (infectiologie/infectieuse...))
    """
    spelist = [clean(x) for x in spelist]
    spelist = [x for x in spelist if x]
    try:
        ret = [
            difflib.get_close_matches(clean(x), self.spe_dic.keys(), 1)
            for x in spelist
                ]
        ret = [self.spe_dic[x[0]] for x in ret if x]
        #print('IN  :', spelist)
        #print('OUT :', [x.name for x in ret])
        #print('')
        return set(ret)
    except Exception:
        logger.exception("Rien")
        #print("Rien pour ", spelist)
        return []


def create_card(**kwargs):
    kwargs["content"] = kwargs['content'].replace("\u001F", "\n")  # question separator
    card = Card(public=True, **kwargs)
    return card


def load_apkg(fn, user):
    """
    Import an anki package.
    :params fn : apkg filename or file-like object to import
    :params user : card are imported with user as author
    """
    cards = []
    specialities = []
    with zipfile.ZipFile(fn, 'r') as zf:
        dirpath = tempfile.mkdtemp()
        zf.extract('collection.anki2', dirpath)
        with sqlite3.connect(os.path.join(dirpath, 'collection.anki2')) as con:
            cursor = con.execute('select tags, flds from notes;')
            for tag, content in cursor.fetchall():
                cards.append(
                    create_card(
                        content=content,
                        author=user,
                    )
                )
                specialities.append(tag)
    cards = Card.objects.bulk_create(cards)
    # TODO when upgrading to django > 1.9 use ids returned by bulk_create
    first_id = Card.objects.order_by('id').last().id - len(cards) + 1
    card_through = []
    for i, spes in enumerate(specialities):
        for spe in self.get_specialities([x for x in spes.split(" ") if x]):
            card_through.append(Card.specialities.through(
                card_id=first_id+i,
                speciality_id=spe.id
            ))
    Card.specialities.through.objects.bulk_create(card_through)
