import difflib
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
fn = 'fiches/endocardite.md'


class Command(BaseCommand):
    help = 'Import .md cards in fiches folder'
    # Dictionnary of spe by word to enhance matches
    spe_dic = { word: spe
               for spe in Speciality.objects.all()
               for word in spe.name.replace("-", " ").split()
               }

    def get_specialities(self, spelist):
        """
        Get close match (remove "ologie" from str for better perfromances (infectiologie/infectieuse...))
        """
        return [
            self.spe_dic[difflib.get_close_matches(x.replace("ologie", ""), self.spe_dic.keys(), 1)[0]]
            for x in spelist
                ]

    def save_fiche(self, **kwargs):
        print(kwargs)
        card = Card(
            title=kwargs["title"],
            section=kwargs["section"],
            content=kwargs["content"]
        )
        card.save()
        card.specialities = self.get_specialities(kwargs['specialities'].split(","))
        card.items = Item.objects.filter(
                          number__in=[ int(x.strip()) for x in kwargs['items'].split(",")]
                      ).all()
        card.save()


    def handle(self, *args, **options):
        Card.objects.all().delete()
        fiche = {}
        fiche["content"] = ""
        ready_to_save = False
        for line in open(fn).readlines():
            line = line.strip()
            for marker, section in mapping:
                if line.startswith(marker):
                    if line and section == "content" :
                        #  append content and flag ready to save
                        ready_to_save = True
                        fiche['content'] += "\n{}".format(line)
                    else:
                        if ready_to_save and fiche['content']:
                            #  save and unflag ready to save
                            self.save_fiche(**fiche)
                            ready_to_save = False
                            fiche["content"] = ""
                        fiche[section] = line.replace(marker, "")
                        break #  break once a marker is found

