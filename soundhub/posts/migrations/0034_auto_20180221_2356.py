# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-02-21 14:56
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0025_remove_user_total_liked'),
        ('posts', '0033_commentlike'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='commenttrack',
            name='instrument',
        ),
        migrations.AddField(
            model_name='commenttrack',
            name='instrument',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='users.Instrument'),
            preserve_default=False,
        ),
    ]
