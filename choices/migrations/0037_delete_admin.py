# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-12 18:45
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('choices', '0036_auto_20161007_1749'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Admin',
        ),
    ]