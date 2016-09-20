# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-20 14:06
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('choices', '0016_talent_audio_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='vendor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='choices.Vendor'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='client',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='choices.Client'),
        ),
    ]