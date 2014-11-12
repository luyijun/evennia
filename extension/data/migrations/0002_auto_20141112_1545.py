# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='object_type_list',
            options={'verbose_name': 'Object Type List', 'verbose_name_plural': 'Object Type List'},
        ),
    ]
