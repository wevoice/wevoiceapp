# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-13 19:03
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('choices', '0011_userprofile'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='website',
        ),
    ]
