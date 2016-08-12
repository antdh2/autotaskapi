# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-10 21:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('autotask_web_app', '0011_picklist'),
    ]

    operations = [
        migrations.CreateModel(
            name='Validation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=254)),
                ('operator', models.CharField(max_length=254)),
                ('value', models.CharField(max_length=254)),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='autotask_web_app.Profile')),
            ],
        ),
    ]