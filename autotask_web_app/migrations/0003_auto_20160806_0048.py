# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-05 23:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('autotask_web_app', '0002_auto_20160806_0045'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='email',
            field=models.EmailField(max_length=254),
        ),
    ]
