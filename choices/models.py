# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User


class Admin(models.Model):
    username = models.TextField()
    password = models.TextField()

    class Meta:
        managed = True
        db_table = 'admin'


class UserProfile(models.Model):
    # This line is required. Links UserProfile to a User model instance.
    user = models.OneToOneField(User)
    client = models.ForeignKey(Client)

    # The additional attributes we wish to include.
    website = models.URLField(blank=True)

    # Override the __unicode__() method to return out something meaningful!
    def __unicode__(self):
        return self.user.username



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
        managed = True
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
        managed = True
        db_table = 'apple'
        verbose_name = 'The Force'
        verbose_name_plural = 'The Force'


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
        managed = True
        db_table = 'cisco'


class Client(models.Model):
    name = models.TextField()
    username = models.TextField()
    password = models.TextField()

    def __unicode__(self):
        return self.name

    class Meta:
        managed = True
        db_table = 'client'
        ordering = ['name']


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
        managed = True
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
        managed = True
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
        managed = True
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
        managed = True
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
        managed = True
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
        managed = True
        db_table = 'kornferry'


class Language(models.Model):
    language = models.TextField()

    class Meta:
        managed = True
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
        managed = True
        db_table = 'main'
        verbose_name = 'Main Talent'
        verbose_name_plural = 'Main Talents'


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
        managed = True
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
        managed = True
        db_table = 'resaas'
        verbose_name = 'Resaas'
        verbose_name_plural = 'Resaas'


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
        managed = True
        db_table = 'thomsonreuters'


class Talent(models.Model):
    welo_id = models.TextField()
    vendor_id = models.TextField()
    vendor_name = models.TextField()
    gender = models.TextField()
    age_range = models.TextField()
    language = models.TextField()
    sample_url = models.TextField()
    pre_approved = models.TextField()
    comment = models.TextField(null=True, blank=True)
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

    def __unicode__(self):
        return self.welo_id

    class Meta:
        managed = True
        db_table = 'talent'
        ordering = ['welo_id']


class Vendor(models.Model):
    name = models.TextField()
    username = models.TextField()
    password = models.TextField()

    def __unicode__(self):
        return self.name

    class Meta:
        managed = True
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
        managed = True
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
        managed = True
        db_table = 'workday'


class Selection(models.Model):
    talent = models.ForeignKey(Talent)
    client = models.ForeignKey(Client)
    STATUS_CHOICES = (
        ("PREAPPROVED", "Pre_Approved"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected")
    )
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="PREAPPROVED")

    def talent_language(self):
        return self.talent.language
    talent_language.short_description = 'Language (fk)'

    def talent_age_range(self):
        return self.talent.age_range
    talent_age_range.short_description = 'Age Range (fk)'

    class Meta:
        unique_together = ('talent', 'client',)
