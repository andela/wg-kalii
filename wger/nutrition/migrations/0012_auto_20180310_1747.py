# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2018-03-10 14:47
from __future__ import unicode_literals

from django.db import migrations
import wger.utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('nutrition', '0011_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mealitem',
            name='time',
            field=wger.utils.fields.Html5TimeField(blank=True, null=True, verbose_name='Time'),
        ),
    ]
