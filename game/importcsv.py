#!/usr/bin/env python
import os
import sys
import csv
import django
from django.db.models.loading import get_model

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print 'Need a csv file!'
        sys.exit(0)

    modelname = sys.argv[1]
    filename = modelname + ".csv"

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "game.settings")
    django.setup()

    try:
        csvfile = open(filename, 'r')
    except:
        print 'Can not open %s!' % filename
        sys.exit(0)

    try:
        reader = csv.reader(csvfile)
    except:
        print 'Can not read %s!' % filename
        sys.exit(0)

    try:
        head = reader.next()
    except StopIteration:
        print 'Can not read %s!' % filename
        sys.exit(0)

    if not head:
        print 'Can not read %s!' % filename
        sys.exit(0)

    modelobj = get_model("data", modelname)
    modelobj.objects.all().delete()

    fields = [field.name for field in modelobj._meta.fields]
    head = [field for field in head if field in fields]

    try:
        line = reader.next()
        while line:
            values = dict(zip(head, line))
            data = modelobj.objects.create(**values)
            data.save()
            line = reader.next()

    except StopIteration:
        pass
