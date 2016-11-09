from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from datetime import datetime
from django.db.models import Avg
from .validators import validate_audiofile_extension, validate_imagefile_extension
from django.db.models.signals import post_save
from django.dispatch import receiver


class Client(models.Model):
    name = models.TextField()
    username = models.TextField()
    logo = models.FileField(blank=True, null=True, upload_to='client_logos', validators=[validate_imagefile_extension])

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
    user = models.OneToOneField(User, primary_key=True)
    client = models.ForeignKey("Client", blank=True, null=True)
    vendor = models.ForeignKey("Vendor", blank=True, null=True)

    def __unicode__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()


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
    rater = models.ForeignKey(User)

    class Meta:
        unique_together = ('talent', 'rater',)

    def __str__(self):
        return str(self.rating)


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
        ("1-15", "1-15"),
        ("16-25", "16-25"),
        ("26-45", "26-45"),
        ("46-75", "46-75"),
        ("75 +", "75 +")
    )

    type = models.CharField(max_length=16, choices=TYPE_CHOICES, default="PR0", blank=True, null=True)
    welo_id = models.TextField(blank=True, null=True)
    vendor = models.ForeignKey("Vendor", default=9, blank=True, null=True)
    gender = models.CharField(max_length=32, choices=GENDER_CHOICES, default="U")
    age_range = models.CharField(max_length=32, choices=AGE_RANGE, default="26-45")
    language = models.ForeignKey("Language", null=True)
    comment = models.TextField(null=True, blank=True)
    audio_file = models.FileField(blank=True, null=True, validators=[validate_audiofile_extension])
    rate = models.TextField(null=True, blank=True)
    average_rating = models.IntegerField(null=True, blank=True)

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

    def times_rated(self):
        return self.rating_set.all().count()
    times_rated.short_description = 'Times Rated'

    def get_average_rating(self):
        return self.rating_set.aggregate(Avg('rating')).values()[0]
    get_average_rating.short_description = 'Rating'

    def get_times_preapproved(self):
        return self.selection_set.filter(status="PREAPPROVED").count()
    get_times_preapproved.short_description = 'Preapproved Total'

    def get_times_accepted(self):
        return self.selection_set.filter(status="APPROVED").count()
    get_times_accepted.short_description = 'Accepted Total'

    def get_times_rejected(self):
        return self.selection_set.filter(status="REJECTED").count()
    get_times_rejected.short_description = 'Rejected Total'

    def __unicode__(self):
        return self.welo_id

    class Meta:
        managed = True
        db_table = 'talent'
        ordering = ['welo_id']

    def save(self, *args, **kwargs):
        self.welo_id = self.audio_file.name.split('.mp3')[0]
        self.average_rating = self.get_average_rating()
        super(Talent, self).save(*args, **kwargs)


class Vendor(models.Model):
    name = models.TextField()
    username = models.TextField()

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

    def talent_language(self):
        return self.talent.language
    talent_language.short_description = 'Language'

    def talent_gender(self):
        return self.talent.gender
    talent_gender.short_description = 'Gender'

    def talent_average_rating(self):
        return self.talent.average_rating
    talent_average_rating.short_description = 'Rating'

    def talent_age_range(self):
        return self.talent.age_range
    talent_age_range.short_description = 'Age Range'

    def total_comments(self):
        comments_count = self.comments.all().count()
        return comments_count

    total_comments.short_description = 'Total Comments'

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

    def save(self, *args, **kwargs):
        from datetime import datetime
        self.last_modified = datetime.now()
        client = self.client
        client.last_modified = datetime.now()
        client.save()
        super(Selection, self).save(*args, **kwargs)


class Comment(models.Model):
    selection = models.ForeignKey(Selection, related_name='comments')
    author = models.ForeignKey(User)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    approved_comment = models.BooleanField(default=False)

    def comment_client(self):
        return self.author.userprofile.client
    comment_client.short_description = 'Client'

    def approve(self):
        self.approved_comment = True
        self.save()

    def __str__(self):
        return str(self.pk)
