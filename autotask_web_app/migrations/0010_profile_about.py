# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-09 09:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('autotask_web_app', '0009_upsell_opportunity_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='about',
            field=models.TextField(default='Enter a biography'),
            preserve_default=False,
        ),
    ]
