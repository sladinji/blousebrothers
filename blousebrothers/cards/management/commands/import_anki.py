
import difflib
import zipfile
import tempfile
import sqlite3
import os
import sys
from glob import glob
import logging
from django.core.management.base import BaseCommand
from blousebrothers.cards.models import Card
from blousebrothers.confs.models import Speciality


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


class Command(BaseCommand):
    help = 'Import .md cards in fiches folder'
    # Dictionnary of spe by word to enhance matches
    spe_dic = {word: spe
               for spe in Speciality.objects.all()
               for word in spe.other_names.split(",")
               }

    def get_specialities(self, spelist):
        """
        Get close match (remove "ologie" from str for better perfromances (infectiologie/infectieuse...))
        """
        try:
            ret = [
                difflib.get_close_matches(x.strip().replace("ologie", ""), self.spe_dic.keys(), 1)
                for x in spelist
                    ]
            ret = [self.spe_dic[x[0]] for x in ret if x]
            print(spelist, ">>", ret)
            return set(ret)
        except Exception:
            logger.exception("Rien")
            print("Rien pour ", spelist)
            return []

    def create_card(self, **kwargs):
        kwargs["content"] = kwargs['content'].replace("\u001F", "\n")  # question separator
        card = Card(public=True, **kwargs)
        return card

    def handle(self, *args, **options):
        Card.objects.all().delete()
        for fn in glob('apkgs/*'):
            cards = []
            specialities = []
            with zipfile.ZipFile(fn, 'r') as zf:
                dirpath = tempfile.mkdtemp()
                zf.extract('collection.anki2', dirpath)
                with sqlite3.connect(os.path.join(dirpath, 'collection.anki2')) as con:
                    cursor = con.execute('select tags, flds from notes;')
                    for tag, content in cursor.fetchall():
                        cards.append(self.create_card(
                            content=content,
                        ))
                        specialities.append(tag)
            cards = Card.objects.bulk_create(cards)
            # TODO when upgrading to django > 1.9 use ids returned by bulk_create
            first_id = Card.objects.order_by('id').last().id - len(cards) + 1
            card_through = []
            for i, spes in enumerate(specialities):
                for spe in self.get_specialities(spes.split(" ")):
                    card_through.append(Card.specialities.through(
                        card_id=first_id+i,
                        speciality_id=spe.id
                    ))
            Card.specialities.through.objects.bulk_create(card_through)
