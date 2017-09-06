import difflib
import zipfile
import tempfile
import sqlite3
import os
import logging
from shutil import rmtree
from blousebrothers.confs.models import Speciality
from blousebrothers.cards.models import Card, Tag

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


def split_spes_tags(tags):
    """
    Get close match (remove "ologie" from str for better perfromances (infectiologie/infectieuse...))
    """
    ctags = [clean(x) for x in tags]
    ctags = [x for x in tags if x]
    spes = [
        difflib.get_close_matches(clean(x), spe_dic.keys(), 1)
        for x in ctags
    ]
    tags = [tags[i] for i, spe in enumerate(spes) if not spe]

    spes = set([spe_dic[x[0]] for x in spes if x])
    return spes, tags


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
    tags = []
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
                tags.append(tag)
    rmtree(dirpath)
    save(cards, tags)
    return len(cards)


def save(cards, tags):
    """
    Save in database cards list and their associated tags list (cards[x] <=> tags[x]).
    :params cards: <list: Card>
    :params tags: <list: string>
    """
    cards = Card.objects.bulk_create(cards)
    # TODO when upgrading to django > 1.9 use ids returned by bulk_create
    first_id = Card.objects.order_by('id').last().id - len(cards) + 1
    card_spes = []
    card_tags = []
    for i, ctags in enumerate(tags):
        spes, tags_words = split_spes_tags([x for x in ctags.split(" ") if x])
        for spe in spes:
            card_spes.append(Card.specialities.through(
                card_id=first_id+i,
                speciality_id=spe.id
            ))
        for tag_word in tags_words:
            card_tags.append(Card.tags.through(
                card_id=first_id+i,
                tag_id=Tag.objects.get_or_create(name=tag_word)[0].id,
            ))
    Card.specialities.through.objects.bulk_create(card_spes)
    Card.tags.through.objects.bulk_create(card_tags)
