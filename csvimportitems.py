import csv
from blousebrothers.confs.models import Item

with open("items_ecn.csv") as f:
        reader = csv.reader(f)
        for row in reader:
            _, created = Item.objects.get_or_create(
                name=row[0],
                number=row[1],
                )
