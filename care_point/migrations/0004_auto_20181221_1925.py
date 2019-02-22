# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-12-21 19:25
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('care_point', '0003_auto_20181221_1916'),
    ]

    operations = [
        migrations.AlterField(
            model_name='decision',
            name='ward',
            field=models.ForeignKey(blank=True, default=1, on_delete=django.db.models.deletion.CASCADE, to='care_point.Ward'),
            preserve_default=False,
        ),
    ]