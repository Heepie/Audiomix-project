# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-12-21 17:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('direct_messages', '0003_auto_20171222_0128'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='is_read',
            field=models.BooleanField(default=False),
        ),
    ]
