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
from django.utils import timezone
from django.conf import settings
from datetime import datetime

DATA_SCHEMA_REVISION = 2


class Admin(models.Model):
    username = models.TextField()
    password = models.TextField()

    class Meta:
        managed = True
        db_table = 'admin'


class Client(models.Model):
    name = models.TextField()
    username = models.TextField()
    password = models.TextField()
    last_modified = models.DateTimeField(null=True, editable=False)

    @property
    def cache_key(self):
        return 'wevoice/%s/client-%s-%s' % (DATA_SCHEMA_REVISION, self.id, self.last_modified)

    def save(self, *args, **kwargs):
        self.last_modified = datetime.now()
        super(Client, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name

    class Meta:
        managed = True
        db_table = 'client'
        ordering = ['name']


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    client = models.ForeignKey("Client", blank=True, null=True)
    vendor = models.ForeignKey("Vendor", blank=True, null=True)

    def first_name(self):
        return self.user.first_name
    first_name.short_description = 'First Name'

    def last_name(self):
        return self.user.last_name
    last_name.short_description = 'Last Name'

    def email(self):
        return self.user.email
    email.short_description = 'Email'

    def is_active(self):
        return self.user.is_active
    is_active.short_description = 'Active'

    def is_superuser(self):
        return self.user.is_superuser
    is_superuser.short_description = 'Superuser'

    def date_joined(self):
        return self.user.date_joined
    date_joined.short_description = 'Joined'

    def last_login(self):
        return self.user.last_login
    last_login.short_description = 'Last Login'

    def is_staff(self):
        return self.user.is_staff
    is_staff.short_description = 'Is Staff'

    def __unicode__(self):
        return self.user.username

    class Meta:
        ordering = ['user__username']


class Language(models.Model):
    language = models.TextField()

    class Meta:
        managed = True
        db_table = 'language'
        ordering = ['language']

    def __unicode__(self):
        return self.language


class Rating(models.Model):
    rating = models.IntegerField(default=0, blank=True, null=True)
    talent = models.ForeignKey('Talent')
    rater = models.ForeignKey('UserProfile')

    class Meta:
        unique_together = ('talent', 'rater',)


class Talent(models.Model):
    TYPE_CHOICES = (
        ("PRO", "Pro Recording"),
        ("HR", "Home Recording"),
        ("TTS", "Text To Speech")
    )

    GENDER_CHOICES = (
        ("M", "Male"),
        ("F", "Female"),
        ("U", "Undeclared")
    )

    AGE_RANGE = (
        ('1', "1-15"),
        ('2', "16-25"),
        ('3', "26-45"),
        ('4', "46-75"),
        ('5', "75 +")
    )

    type = models.CharField(max_length=16, choices=TYPE_CHOICES, default="PR0", blank=True, null=True)
    welo_id = models.TextField(blank=True, null=True)
    old_talent_id = models.IntegerField(default=0, blank=True, null=True)
    vendor = models.ForeignKey("Vendor", default=9, blank=True, null=True)
    gender = models.CharField(max_length=32, choices=GENDER_CHOICES, default=1, blank=True, null=True)
    age_range = models.CharField(max_length=32, choices=AGE_RANGE, default=3, blank=True, null=True)
    language = models.ForeignKey("Language", blank=True, null=True)
    audio_file = models.FileField(blank=True, null=True)
    times_rated = models.IntegerField(default=0, blank=True, null=True)
    total_rating = models.IntegerField(default=0, blank=True, null=True)

    def audio_file_player(self):
        """audio player tag for admin"""
        if self.audio_file:
            file_url = self.audio_file.url
            player_string = \
                '<div class="simple-player-container" style="background-color: #ffffff;">' \
                '<audio class="player" preload="none" src="%s"></audio>' \
                '</div>' % file_url
            return player_string

    audio_file_player.allow_tags = True
    audio_file_player.short_description = "Audio player"

    def average_rating(self):
        if self.times_rated > 0:
            return int(round(float(self.total_rating) / float(self.times_rated)))

    average_rating.short_description = "Rating"

    comment = models.TextField(null=True, blank=True)
    allclients = models.TextField(blank=True, null=True)
    rate = models.TextField(null=True, blank=True)

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
        ordering = ['name']


class Selection(models.Model):
    STATUS_CHOICES = (
        ("PREAPPROVED", "Pre_Approved"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected")
    )
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="PREAPPROVED")
    talent = models.ForeignKey(Talent)
    client = models.ForeignKey(Client)
    last_modified = models.DateTimeField(null=True, editable=False)

    def talent_language(self):
        return self.talent.language
    talent_language.short_description = 'Language'

    def talent_gender(self):
        return self.talent.gender
    talent_gender.short_description = 'Gender'

    def talent_age_range(self):
        return self.talent.age_range
    talent_age_range.short_description = 'Age Range'

    def talent_vendor(self):
        return self.talent.vendor
    talent_vendor.short_description = 'Vendor'

    def audio_file_player(self):
        """audio player tag for admin"""
        if self.talent.audio_file:
            file_url = settings.MEDIA_URL + str(self.talent.audio_file)
            player_string = \
                '<div class="simple-player-container" style="background-color: #ffffff;">' \
                '<audio class="player" preload="none" src="%s"></audio>' \
                '</div>' % file_url
            return player_string

    audio_file_player.allow_tags = True
    audio_file_player.short_description = "Audio player"

    class Meta:
        unique_together = ('talent', 'client',)

    def __unicode__(self):
        return self.talent.welo_id + ": " + self.client.username

    @property
    def cache_key(self):
        return 'wevoice/%s/selection-%s-%s' % (DATA_SCHEMA_REVISION, self.id, self.last_modified)

    def save(self, *args, **kwargs):
        from datetime import datetime
        self.last_modified = datetime.now()
        client = self.client
        client.last_modified = datetime.now()
        client.save()
        super(Selection, self).save(*args, **kwargs)


class Comment(models.Model):
    post = models.ForeignKey(Selection, related_name='comments')
    author = models.ForeignKey(UserProfile)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    approved_comment = models.BooleanField(default=False)

    def approve(self):
        self.approved_comment = True
        self.save()

    def __str__(self):
        return self.text
