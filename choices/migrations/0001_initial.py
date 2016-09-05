# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-05 18:37
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Admin',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('username', models.TextField()),
                ('password', models.TextField()),
            ],
            options={
                'db_table': 'admin',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Anheuserbusch',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('talent', models.TextField()),
                ('client', models.TextField()),
                ('gender', models.TextField()),
                ('age_range', models.TextField()),
                ('language', models.TextField()),
                ('sample_url', models.TextField()),
                ('accepted', models.TextField()),
                ('comment', models.TextField()),
            ],
            options={
                'db_table': 'anheuserbusch',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Apple',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('talent', models.TextField()),
                ('client', models.TextField()),
                ('gender', models.TextField()),
                ('age_range', models.TextField()),
                ('language', models.TextField()),
                ('sample_url', models.TextField()),
                ('accepted', models.TextField()),
                ('comment', models.TextField()),
            ],
            options={
                'db_table': 'apple',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='AuthGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=80, unique=True)),
            ],
            options={
                'db_table': 'auth_group',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='AuthGroupPermissions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='choices.AuthGroup')),
            ],
            options={
                'db_table': 'auth_group_permissions',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='AuthPermission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('codename', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'auth_permission',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='AuthUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128)),
                ('last_login', models.DateTimeField(blank=True, null=True)),
                ('is_superuser', models.BooleanField()),
                ('username', models.CharField(max_length=150, unique=True)),
                ('first_name', models.CharField(max_length=30)),
                ('last_name', models.CharField(max_length=30)),
                ('email', models.CharField(max_length=254)),
                ('is_staff', models.BooleanField()),
                ('is_active', models.BooleanField()),
                ('date_joined', models.DateTimeField()),
            ],
            options={
                'db_table': 'auth_user',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='AuthUserGroups',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='choices.AuthGroup')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='choices.AuthUser')),
            ],
            options={
                'db_table': 'auth_user_groups',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='AuthUserUserPermissions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('permission', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='choices.AuthPermission')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='choices.AuthUser')),
            ],
            options={
                'db_table': 'auth_user_user_permissions',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Cisco',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('talent', models.TextField()),
                ('client', models.TextField()),
                ('gender', models.TextField()),
                ('age_range', models.TextField()),
                ('language', models.TextField()),
                ('sample_url', models.TextField()),
                ('accepted', models.TextField()),
                ('comment', models.TextField()),
            ],
            options={
                'db_table': 'cisco',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('name', models.TextField()),
                ('username', models.TextField()),
                ('password', models.TextField()),
            ],
            options={
                'db_table': 'client',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='DjangoAdminLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action_time', models.DateTimeField()),
                ('object_id', models.TextField(blank=True, null=True)),
                ('object_repr', models.CharField(max_length=200)),
                ('action_flag', models.SmallIntegerField()),
                ('change_message', models.TextField()),
            ],
            options={
                'db_table': 'django_admin_log',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='DjangoContentType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('app_label', models.CharField(max_length=100)),
                ('model', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'django_content_type',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='DjangoMigrations',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('app', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('applied', models.DateTimeField()),
            ],
            options={
                'db_table': 'django_migrations',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='DjangoSession',
            fields=[
                ('session_key', models.CharField(max_length=40, primary_key=True, serialize=False)),
                ('session_data', models.TextField()),
                ('expire_date', models.DateTimeField()),
            ],
            options={
                'db_table': 'django_session',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Esterline',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('talent', models.TextField()),
                ('client', models.TextField()),
                ('gender', models.TextField()),
                ('age_range', models.TextField()),
                ('language', models.TextField()),
                ('sample_url', models.TextField()),
                ('accepted', models.TextField()),
                ('comment', models.TextField()),
            ],
            options={
                'db_table': 'esterline',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Google',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('talent', models.TextField()),
                ('client', models.TextField()),
                ('gender', models.TextField()),
                ('age_range', models.TextField()),
                ('language', models.TextField()),
                ('sample_url', models.TextField()),
                ('accepted', models.TextField()),
                ('comment', models.TextField()),
            ],
            options={
                'db_table': 'google',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Gt',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('talent', models.TextField()),
                ('client', models.TextField()),
                ('gender', models.TextField()),
                ('age_range', models.TextField()),
                ('language', models.TextField()),
                ('sample_url', models.TextField()),
                ('accepted', models.TextField()),
                ('comment', models.TextField()),
            ],
            options={
                'db_table': 'gt',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Hd',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('talent', models.TextField()),
                ('client', models.TextField()),
                ('gender', models.TextField()),
                ('age_range', models.TextField()),
                ('language', models.TextField()),
                ('sample_url', models.TextField()),
                ('accepted', models.TextField()),
                ('comment', models.TextField()),
            ],
            options={
                'db_table': 'hd',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Jdeere',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('talent', models.TextField()),
                ('client', models.TextField()),
                ('gender', models.TextField()),
                ('age_range', models.TextField()),
                ('language', models.TextField()),
                ('sample_url', models.TextField()),
                ('accepted', models.TextField()),
                ('comment', models.TextField()),
            ],
            options={
                'db_table': 'jdeere',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Kornferry',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('talent', models.TextField()),
                ('client', models.TextField()),
                ('gender', models.TextField()),
                ('age_range', models.TextField()),
                ('language', models.TextField()),
                ('sample_url', models.TextField()),
                ('accepted', models.TextField()),
                ('comment', models.TextField()),
            ],
            options={
                'db_table': 'kornferry',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False, unique=True)),
                ('language', models.TextField()),
            ],
            options={
                'db_table': 'language',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Main',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('talent', models.TextField()),
                ('client', models.TextField()),
                ('gender', models.TextField()),
                ('age_range', models.TextField()),
                ('language', models.TextField()),
                ('sample_url', models.TextField()),
                ('accepted', models.TextField()),
                ('comment', models.TextField()),
            ],
            options={
                'db_table': 'main',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Nrm',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('talent', models.TextField()),
                ('client', models.TextField()),
                ('gender', models.TextField()),
                ('age_range', models.TextField()),
                ('language', models.TextField()),
                ('sample_url', models.TextField()),
                ('accepted', models.TextField()),
                ('comment', models.TextField()),
            ],
            options={
                'db_table': 'nrm',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Resaas',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('talent', models.TextField()),
                ('client', models.TextField()),
                ('gender', models.TextField()),
                ('age_range', models.TextField()),
                ('language', models.TextField()),
                ('sample_url', models.TextField()),
                ('accepted', models.TextField()),
                ('comment', models.TextField()),
            ],
            options={
                'db_table': 'resaas',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Talent',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('welo_id', models.TextField()),
                ('vendor_id', models.TextField()),
                ('vendor_name', models.TextField()),
                ('gender', models.TextField()),
                ('age_range', models.TextField()),
                ('language', models.TextField()),
                ('sample_url', models.TextField()),
                ('pre_approved', models.TextField()),
                ('comment', models.TextField()),
                ('allclients', models.TextField()),
                ('vmware', models.TextField()),
                ('google', models.TextField()),
                ('gt', models.TextField()),
                ('nrm', models.TextField()),
                ('hr', models.TextField()),
                ('rate', models.TextField()),
                ('hd', models.TextField()),
                ('workday', models.TextField()),
                ('tts', models.TextField()),
                ('cisco', models.TextField()),
                ('kornferry', models.TextField()),
                ('jdeere', models.TextField()),
                ('anheuserbusch', models.TextField()),
                ('apple', models.TextField()),
                ('thomsonreuters', models.TextField()),
                ('esterline', models.TextField()),
            ],
            options={
                'db_table': 'talent',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Thomsonreuters',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('talent', models.TextField()),
                ('client', models.TextField()),
                ('gender', models.TextField()),
                ('age_range', models.TextField()),
                ('language', models.TextField()),
                ('sample_url', models.TextField()),
                ('accepted', models.TextField()),
                ('comment', models.TextField()),
            ],
            options={
                'db_table': 'thomsonreuters',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Vendor',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('name', models.TextField()),
                ('username', models.TextField()),
                ('password', models.TextField()),
            ],
            options={
                'db_table': 'vendor',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Vmware',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('talent', models.TextField()),
                ('client', models.TextField()),
                ('gender', models.TextField()),
                ('age_range', models.TextField()),
                ('language', models.TextField()),
                ('sample_url', models.TextField()),
                ('accepted', models.TextField()),
                ('comment', models.TextField()),
            ],
            options={
                'db_table': 'vmware',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Workday',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('talent', models.TextField()),
                ('client', models.TextField()),
                ('gender', models.TextField()),
                ('age_range', models.TextField()),
                ('language', models.TextField()),
                ('sample_url', models.TextField()),
                ('accepted', models.TextField()),
                ('comment', models.TextField()),
            ],
            options={
                'db_table': 'workday',
                'managed': True,
            },
        ),
        migrations.AlterUniqueTogether(
            name='djangocontenttype',
            unique_together=set([('app_label', 'model')]),
        ),
        migrations.AddField(
            model_name='djangoadminlog',
            name='content_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='choices.DjangoContentType'),
        ),
        migrations.AddField(
            model_name='djangoadminlog',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='choices.AuthUser'),
        ),
        migrations.AddField(
            model_name='authpermission',
            name='content_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='choices.DjangoContentType'),
        ),
        migrations.AddField(
            model_name='authgrouppermissions',
            name='permission',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='choices.AuthPermission'),
        ),
        migrations.AlterUniqueTogether(
            name='authuseruserpermissions',
            unique_together=set([('user', 'permission')]),
        ),
        migrations.AlterUniqueTogether(
            name='authusergroups',
            unique_together=set([('user', 'group')]),
        ),
        migrations.AlterUniqueTogether(
            name='authpermission',
            unique_together=set([('content_type', 'codename')]),
        ),
        migrations.AlterUniqueTogether(
            name='authgrouppermissions',
            unique_together=set([('group', 'permission')]),
        ),
    ]
