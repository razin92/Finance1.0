# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-10-24 18:41
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lib', '0002_auto_20170914_1615'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='person',
            options={'ordering': ['firstname', 'secondname']},
        ),
        migrations.AlterModelOptions(
            name='pouch',
            options={'ordering': ['name']},
        ),
    ]
