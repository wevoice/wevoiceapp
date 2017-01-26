# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-01-26 19:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('choices', '0006_talentsbyvendor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='language',
            name='code',
            field=models.CharField(blank=True, max_length=32, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='talent',
            name='audio_file_sha',
            field=models.CharField(blank=True, max_length=40, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='talent',
            name='welo_id',
            field=models.TextField(blank=True, null=True, unique=True),
        ),
    ]
