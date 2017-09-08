import difflib
import zipfile
import tempfile
import sqlite3
import os
import logging
import threading
from shutil import rmtree
from django.core.files import File
from blousebrothers.confs.models import Speciality
from .models import Card, Tag, AnkiPackage, AnkiImage

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


def create_cards(**kwargs):
    content = kwargs.pop('content')
    length = len(content.split("\u001F"))
    contents = iter(content.split("\u001F")) # question separator

    if length == 3:
            return [Card(
                public=False,
                content="\n".join([next(contents), next(contents), next(contents),]),
                **kwargs
            )]

    cards = []
    for content in contents:
        if not content:
            break
        card = Card(public=False, content="\n".join([content, next(contents)]), **kwargs)
        cards.append(card)
    return cards


class Importer():
    """
    Replace media address in anki content with the address where we saved it.
    """

    def __init__(self, map, anki_package):
        """
        :params map: { old_path: new_path }
        """
        self.map = map
        self.anki_package = anki_package

    def update(self, content):
        """
        Replace old media path by new ones in content.
        """
        for k, v in self.map.items():
            content = content.replace("src='{}'".format(k), "src='{}'".format(v))
            content = content.replace('src="{}"'.format(k), 'src="{}"'.format(v))
        return content


def get_importer(fd, user, dirpath, filename):
    """
    Importer factory, save media and return an Importer object to update card content.
    """
    pkg = AnkiPackage(owner=user)
    pkg.save()
    afile = File(fd)
    pkg.file.save(filename, afile)
    new_map = {}
    with open(os.path.join(dirpath, "media")) as media:
        dic = eval(media.read())
        for k, v in dic.items():
            ai = AnkiImage(package=pkg)
            ai.save()
            with open(os.path.join(dirpath, k), "rb") as f:
                ifile = File(f)
                ai.image.save(v, ifile)
            new_map.update(**{v: ai.image.url})
    return Importer(new_map, pkg)

def work(tmpf, user, filename):
    try:
        cards = []
        tags = []
        with zipfile.ZipFile(tmpf, 'r') as zf:
            dirpath = tempfile.mkdtemp()
            zf.extractall(dirpath)
            importer = get_importer(tmpf, user, dirpath, filename)  # upload media and archive on amazon
            with sqlite3.connect(os.path.join(dirpath, 'collection.anki2')) as con:
                cursor = con.execute('select id, tags, flds from notes;')
                for pkg_id, tag, content in cursor.fetchall():
                    content = importer.update(content)  # update image address with new amazon ones
                    for card in create_cards(
                        content=content,
                        author=user,
                        anki_pkg=importer.anki_package,
                        anki_id=pkg_id,
                    ):
                        cards.append(card)
                        tags.append(tag)
        tmpf.close()  # tmpfile is removed on close
        rmtree(dirpath)
        save(cards, tags)
        return len(cards)
    except:
        logger.exception("Anki thread import failed")

def load_apkg(fd, user):
    """
    Import an anki package.
    :params fd : apkg file-like object to import
    :params user : card are imported with user as author
    """
    tmpf = tempfile.TemporaryFile()
    tmpf.write(fd.read())
    tmpf.seek(0)
    filename = os.path.basename(fd.name)
    threading.Thread(target=work, args=(tmpf, user, filename)).start()

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
