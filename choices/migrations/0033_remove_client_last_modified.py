# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-05 15:57
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('choices', '0032_remove_selection_last_modified'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='client',
            name='last_modified',
        ),
    ]