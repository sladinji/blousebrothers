import difflib
from glob import glob
from blousebrothers.cards.models import Card, Tag
from blousebrothers.confs.models import Item, Speciality


mapping = (
    ("####", "specialities"),
    ("###", "items"),
    ("##", "title"),
    ("#", "section"),
    ("", "content"),
)


spe_dic = {word: spe
           for spe in Speciality.objects.all()
           for word in spe.name.replace("-", " ").split()
           }


def get_specialities(spelist):
    """
    Get close match (remove "ologie" from str for better perfromances (infectiologie/infectieuse...))
    """
    ret = [
        spe_dic[difflib.get_close_matches(x.strip().replace("ologie", ""), spe_dic.keys(), 1)[0]]
        for x in spelist
            ]
    return ret


def create_objects(user, lcards, lspes, ltags, litems, **kwargs):
    kwargs["content"] = kwargs['content'].replace("~", "@@")
    items = kwargs.pop('items')
    specialities = kwargs.pop('specialities')
    section = kwargs.pop('section', False)
    title = kwargs.pop('title', False)

    access = user.username == "BlouseBrothers"
    lcards.append(Card(public=access, author=user, **kwargs))
    lspes.append(get_specialities(specialities.split(",")))
    litems.append(Item.objects.filter(
                        number__in=[int(x.strip()) for x in items.split(",")]
                    ).all())
    card_tags = []
    for tag in section, title:
        if tag:
            card_tags.append(Tag.objects.get_or_create(name=tag)[0],)
    ltags.append(card_tags)
    return lcards, lspes, ltags, litems


def save_objects(lcards, lspes, ltags, litems, **kwargs):
    cards = Card.objects.bulk_create(lcards)
    # TODO when upgrading to django > 1.9 use ids returned by bulk_create
    first_id = Card.objects.order_by('id').last().id - len(cards) + 1
    card_ids = range(first_id, first_id + len(cards))
    card_spes, card_tags, card_items = [], [], []
    for card_id, spes, tags, items in zip(card_ids, lspes, ltags, litems):
        for spe in spes:
            card_spes.append(Card.specialities.through(
                card_id=card_id,
                speciality_id=spe.id
            ))
        for tag in tags:
            card_tags.append(Card.tags.through(
                card_id=card_id,
                tag_id=tag.id
            ))
        for item in items:
            card_items.append(Card.items.through(
                card_id=card_id,
                item_id=item.id
            ))
    Card.specialities.through.objects.bulk_create(card_spes)
    Card.tags.through.objects.bulk_create(card_tags)
    Card.items.through.objects.bulk_create(card_items)


def load(fd, user):
    lcards, lspes, ltags, litems = [], [], [], []
    fiche = {}
    fiche["content"] = ""
    ready_to_save = False
    for line in fd.readlines():
        line = line.decode("utf-8")
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
                        lcards, lspes, ltags, litems = create_objects(
                            user, lcards, lspes, ltags, litems, **fiche)
                        ready_to_save = False
                        fiche["content"] = ""
                    fiche[section] = line.replace(marker, "")
                    break  # break once a marker is found
    save_objects(lcards, lspes, ltags, litems)
