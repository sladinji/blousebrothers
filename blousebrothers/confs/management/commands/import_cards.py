import difflib
from glob import glob
from django.core.management.base import BaseCommand
from django.contrib.flatpages.models import FlatPage
from blousebrothers.cards.models import Card
from blousebrothers.confs.models import Item, Speciality


mapping = (
    ("####", "specialities"),
    ("###", "items"),
    ("##", "title"),
    ("#", "section"),
    ("", "content"),
)
fn = 'fiches/Item 231 - Insuffisance aortique.txt'


class Command(BaseCommand):
    help = 'Import .md cards in fiches folder'
    # Dictionnary of spe by word to enhance matches
    spe_dic = {word: spe
               for spe in Speciality.objects.all()
               for word in spe.name.replace("-", " ").split()
               }

    def get_specialities(self, spelist):
        """
        Get close match (remove "ologie" from str for better perfromances (infectiologie/infectieuse...))
        """
        ret= [
            self.spe_dic[difflib.get_close_matches(x.strip().replace("ologie", ""), self.spe_dic.keys(), 1)[0]]
            for x in spelist
                ]
        print(spelist, ">>", ret)
        return ret

    def save_fiche(self, **kwargs):
        kwargs["content"] = kwargs['content'].replace("~", "@@")
        items = kwargs.pop('items')
        specialities = kwargs.pop('specialities')
        card = Card(**kwargs)
        card.save()
        card.specialities = self.get_specialities(specialities.split(","))
        card.items = Item.objects.filter(
                          number__in=[int(x.strip()) for x in items.split(",")]
                      ).all()
        card.save()

    def handle(self, *args, **options):
        Card.objects.all().delete()
        for fn in glob('fiches/*'):
            fiche = {}
            fiche["content"] = ""
            ready_to_save = False
            print(">> importing %s" % fn)
            for line in open(fn).readlines():
                line = line.strip()
                for marker, section in mapping:
                    if line.startswith(marker):
                        if line and section == "content":
                            # append content and flag ready to save
                            ready_to_save = True
                            fiche['content'] += "\n{}".format(line)
                        else:
                            if ready_to_save and fiche['content']:
                                # save and unflag ready to save
                                self.save_fiche(**fiche)
                                ready_to_save = False
                                fiche["content"] = ""
                            fiche[section] = line.replace(marker, "")
                            break  # break once a marker is found
