# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-01-19 05:55
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0022_auto_20180118_2321'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='fb_id',
            new_name='oauth_id',
        ),
    ]
