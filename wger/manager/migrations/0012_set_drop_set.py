# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2018-03-08 17:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0011_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='set',
            name='drop_set',
            field=models.BooleanField(default=False, verbose_name='Drop set'),
        ),
    ]
