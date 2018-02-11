# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-02-08 02:26
from __future__ import unicode_literals

from django.db import migrations, models
import posts.directory_path


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0030_auto_20180201_1646'),
    ]

    operations = [
        migrations.AddField(
            model_name='commenttrack',
            name='comment_track_base',
            field=models.ImageField(blank=True, null=True, upload_to=posts.directory_path.comment_track_waveform_base_directory_path),
        ),
        migrations.AddField(
            model_name='commenttrack',
            name='comment_track_cover',
            field=models.ImageField(blank=True, null=True, upload_to=posts.directory_path.comment_track_waveform_cover_directory_path),
        ),
    ]