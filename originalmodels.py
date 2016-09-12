# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models


class Admin(models.Model):
    username = models.TextField()
    password = models.TextField()

    class Meta:
        managed = False
        db_table = 'admin'


class Anheuserbusch(models.Model):
    talent = models.TextField()
    client = models.TextField()
    gender = models.TextField()
    age_range = models.TextField()
    language = models.TextField()
    sample_url = models.TextField()
    accepted = models.TextField()
    comment = models.TextField()

    class Meta:
        managed = False
        db_table = 'anheuserbusch'


class Apple(models.Model):
    talent = models.TextField()
    client = models.TextField()
    gender = models.TextField()
    age_range = models.TextField()
    language = models.TextField()
    sample_url = models.TextField()
    accepted = models.TextField()
    comment = models.TextField()

    class Meta:
        managed = False
        db_table = 'apple'


class Cisco(models.Model):
    talent = models.TextField()
    client = models.TextField()
    gender = models.TextField()
    age_range = models.TextField()
    language = models.TextField()
    sample_url = models.TextField()
    accepted = models.TextField()
    comment = models.TextField()

    class Meta:
        managed = False
        db_table = 'cisco'


class Client(models.Model):
    name = models.TextField()
    username = models.TextField()
    password = models.TextField()

    class Meta:
        managed = False
        db_table = 'client'


class Esterline(models.Model):
    talent = models.TextField()
    client = models.TextField()
    gender = models.TextField()
    age_range = models.TextField()
    language = models.TextField()
    sample_url = models.TextField()
    accepted = models.TextField()
    comment = models.TextField()

    class Meta:
        managed = False
        db_table = 'esterline'


class Google(models.Model):
    talent = models.TextField()
    client = models.TextField()
    gender = models.TextField()
    age_range = models.TextField()
    language = models.TextField()
    sample_url = models.TextField()
    accepted = models.TextField()
    comment = models.TextField()

    class Meta:
        managed = False
        db_table = 'google'


class Gt(models.Model):
    talent = models.TextField()
    client = models.TextField()
    gender = models.TextField()
    age_range = models.TextField()
    language = models.TextField()
    sample_url = models.TextField()
    accepted = models.TextField()
    comment = models.TextField()

    class Meta:
        managed = False
        db_table = 'gt'


class Hd(models.Model):
    talent = models.TextField()
    client = models.TextField()
    gender = models.TextField()
    age_range = models.TextField()
    language = models.TextField()
    sample_url = models.TextField()
    accepted = models.TextField()
    comment = models.TextField()

    class Meta:
        managed = False
        db_table = 'hd'


class Jdeere(models.Model):
    talent = models.TextField()
    client = models.TextField()
    gender = models.TextField()
    age_range = models.TextField()
    language = models.TextField()
    sample_url = models.TextField()
    accepted = models.TextField()
    comment = models.TextField()

    class Meta:
        managed = False
        db_table = 'jdeere'


class Kornferry(models.Model):
    talent = models.TextField()
    client = models.TextField()
    gender = models.TextField()
    age_range = models.TextField()
    language = models.TextField()
    sample_url = models.TextField()
    accepted = models.TextField()
    comment = models.TextField()

    class Meta:
        managed = False
        db_table = 'kornferry'


class Language(models.Model):
    id = models.AutoField(unique=True)
    language = models.TextField()

    class Meta:
        managed = False
        db_table = 'language'


class Main(models.Model):
    talent = models.TextField()
    client = models.TextField()
    gender = models.TextField()
    age_range = models.TextField()
    language = models.TextField()
    sample_url = models.TextField()
    accepted = models.TextField()
    comment = models.TextField()

    class Meta:
        managed = False
        db_table = 'main'


class Nrm(models.Model):
    talent = models.TextField()
    client = models.TextField()
    gender = models.TextField()
    age_range = models.TextField()
    language = models.TextField()
    sample_url = models.TextField()
    accepted = models.TextField()
    comment = models.TextField()

    class Meta:
        managed = False
        db_table = 'nrm'


class Resaas(models.Model):
    talent = models.TextField()
    client = models.TextField()
    gender = models.TextField()
    age_range = models.TextField()
    language = models.TextField()
    sample_url = models.TextField()
    accepted = models.TextField()
    comment = models.TextField()

    class Meta:
        managed = False
        db_table = 'resaas'


class Talent(models.Model):
    welo_id = models.TextField()
    vendor_id = models.TextField()
    vendor_name = models.TextField()
    gender = models.TextField()
    age_range = models.TextField()
    language = models.TextField()
    sample_url = models.TextField()
    pre_approved = models.TextField()
    comment = models.TextField()
    allclients = models.TextField()
    vmware = models.TextField()
    google = models.TextField()
    gt = models.TextField()
    nrm = models.TextField()
    hr = models.TextField()
    rate = models.TextField()
    hd = models.TextField()
    workday = models.TextField()
    tts = models.TextField()
    cisco = models.TextField()
    kornferry = models.TextField()
    jdeere = models.TextField()
    anheuserbusch = models.TextField()
    apple = models.TextField()
    thomsonreuters = models.TextField()
    esterline = models.TextField()

    class Meta:
        managed = False
        db_table = 'talent'


class Thomsonreuters(models.Model):
    talent = models.TextField()
    client = models.TextField()
    gender = models.TextField()
    age_range = models.TextField()
    language = models.TextField()
    sample_url = models.TextField()
    accepted = models.TextField()
    comment = models.TextField()

    class Meta:
        managed = False
        db_table = 'thomsonreuters'


class Vendor(models.Model):
    name = models.TextField()
    username = models.TextField()
    password = models.TextField()

    class Meta:
        managed = False
        db_table = 'vendor'


class Vmware(models.Model):
    talent = models.TextField()
    client = models.TextField()
    gender = models.TextField()
    age_range = models.TextField()
    language = models.TextField()
    sample_url = models.TextField()
    accepted = models.TextField()
    comment = models.TextField()

    class Meta:
        managed = False
        db_table = 'vmware'


class Workday(models.Model):
    talent = models.TextField()
    client = models.TextField()
    gender = models.TextField()
    age_range = models.TextField()
    language = models.TextField()
    sample_url = models.TextField()
    accepted = models.TextField()
    comment = models.TextField()

    class Meta:
        managed = False
        db_table = 'workday'
