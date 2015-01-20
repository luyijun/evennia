# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Object_Type_List',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('db_key', models.CharField(max_length=255, db_index=True)),
                ('db_name', models.CharField(max_length=255)),
                ('db_typeclass_path', models.CharField(max_length=255)),
                ('db_desc', models.TextField(blank=True)),
                ('db_bind_type', models.IntegerField(default=0, blank=True)),
                ('db_unique', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
