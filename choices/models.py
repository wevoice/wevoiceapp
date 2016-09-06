# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = True` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models


class Admin(models.Model):
    id = models.BigIntegerField(primary_key=True)
    username = models.TextField()
    password = models.TextField()

    class Meta:
        managed = True
        db_table = 'admin'


class Anheuserbusch(models.Model):
    id = models.BigIntegerField(primary_key=True)
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
    id = models.BigIntegerField(primary_key=True)
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
        verbose_name = 'Apple'
        verbose_name_plural = 'Apple'

    def __unicode__(self):
        return self.name


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=80)

    class Meta:
        managed = True
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = True
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = True
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = True
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = True
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = True
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class Cisco(models.Model):
    id = models.BigIntegerField(primary_key=True)
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
    id = models.BigIntegerField(primary_key=True)
    name = models.TextField()
    username = models.TextField()
    password = models.TextField()

    class Meta:
        managed = True
        db_table = 'client'

    def __unicode__(self):
        return self.name


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = True
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = True
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = True
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = True
        db_table = 'django_session'


class Esterline(models.Model):
    id = models.BigIntegerField(primary_key=True)
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
    id = models.BigIntegerField(primary_key=True)
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
    id = models.BigIntegerField(primary_key=True)
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
    id = models.BigIntegerField(primary_key=True)
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
    id = models.BigIntegerField(primary_key=True)
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
    id = models.BigIntegerField(primary_key=True)
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
    id = models.BigIntegerField(unique=True, primary_key=True)
    language = models.TextField()

    class Meta:
        managed = True
        db_table = 'language'

    def __unicode__(self):
        return self.language


class Main(models.Model):
    id = models.BigIntegerField(primary_key=True)
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

    def __unicode__(self):
        return self.talent


class Nrm(models.Model):
    id = models.BigIntegerField(primary_key=True)
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
    id = models.BigIntegerField(primary_key=True)
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


class Talent(models.Model):
    id = models.BigIntegerField(primary_key=True)
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
        managed = True
        db_table = 'talent'

    def __unicode__(self):
        return self.welo_id


class Thomsonreuters(models.Model):
    id = models.BigIntegerField(primary_key=True)
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


class Vendor(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.TextField()
    username = models.TextField()
    password = models.TextField()

    class Meta:
        managed = True
        db_table = 'vendor'

    def __unicode__(self):
        return self.name


class Vmware(models.Model):
    id = models.BigIntegerField(primary_key=True)
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
    id = models.BigIntegerField(primary_key=True)
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
