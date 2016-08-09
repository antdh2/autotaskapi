# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-07 21:54
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('autotask_web_app', '0004_auto_20160806_0107'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookingInDetails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_id', models.CharField(max_length=254)),
                ('ticket_id', models.CharField(max_length=254)),
                ('software_collected', models.CharField(max_length=254)),
                ('chargers_collected', models.CharField(max_length=254)),
                ('cables_collected', models.CharField(max_length=254)),
                ('item', models.CharField(max_length=254)),
                ('passwords', models.CharField(max_length=254)),
                ('action_required', models.CharField(max_length=254)),
                ('condition', models.CharField(max_length=254)),
                ('ifotheraction', models.CharField(max_length=254)),
                ('damaged', models.CharField(max_length=254)),
                ('front', models.CharField(max_length=254)),
                ('lside', models.CharField(max_length=254)),
                ('top', models.CharField(max_length=254)),
                ('bottom', models.CharField(max_length=254)),
                ('screen', models.CharField(max_length=254)),
                ('cables', models.CharField(max_length=254)),
                ('keyboard', models.CharField(max_length=254)),
                ('other', models.CharField(max_length=254)),
                ('rside', models.CharField(max_length=254)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]