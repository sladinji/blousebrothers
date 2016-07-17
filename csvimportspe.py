import csv
from blousebrothers.confs.models import Speciality

with open("speciality.csv") as f:
        reader = csv.reader(f)
        for row in reader:
            _, created = Speciality.objects.get_or_create(
                name=row[0],
                )
