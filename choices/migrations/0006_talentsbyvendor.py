# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-01-25 19:01
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('choices', '0005_auto_20170117_1836'),
    ]

    operations = [
        migrations.CreateModel(
            name='TalentsByVendor',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('choices.talent',),
        ),
    ]
