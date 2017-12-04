# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-12-04 12:13
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salary', '0005_auto_20171002_1621'),
    ]

    operations = [
        migrations.AddField(
            model_name='worker',
            name='salary',
            field=models.IntegerField(default=650000),
        ),
        migrations.AlterField(
            model_name='total',
            name='date',
            field=models.DateField(default=datetime.datetime(2017, 12, 1, 12, 13, 12, 675429)),
        ),
        migrations.AlterField(
            model_name='workcalc',
            name='time_range',
            field=models.CharField(choices=[('Час', 'hour'), ('Процент', 'percent'), ('Оклад', 'salary'), ('Месяц', 'month'), ('День', 'day')], max_length=20),
        ),
    ]
