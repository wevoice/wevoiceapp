# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-05 15:50
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('choices', '0031_auto_20160930_2054'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='selection',
            name='last_modified',
        ),
    ]
