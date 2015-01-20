# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0002_auto_20141112_1545'),
    ]

    operations = [
        migrations.CreateModel(
            name='Object_Creator_Types',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('db_key', models.IntegerField(default=0)),
                ('db_obj_list', models.TextField(default=b'', blank=True)),
                ('db_command', models.CharField(max_length=255)),
                ('db_question', models.TextField(default=b'', blank=True)),
            ],
            options={
                'verbose_name': 'Object Creator Types',
                'verbose_name_plural': 'Object Creator Types',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Portable_Object_Types',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('db_key', models.IntegerField(default=0)),
                ('db_bind_type', models.IntegerField(default=0)),
                ('db_unique', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Portable Object Types',
                'verbose_name_plural': 'Portable Object Types',
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='object_type_list',
            name='db_bind_type',
        ),
        migrations.RemoveField(
            model_name='object_type_list',
            name='db_unique',
        ),
        migrations.AddField(
            model_name='object_type_list',
            name='db_category',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='object_type_list',
            name='db_desc',
            field=models.TextField(default=b'', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='object_type_list',
            name='db_key',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
