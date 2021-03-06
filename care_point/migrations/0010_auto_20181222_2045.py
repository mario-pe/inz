# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-12-22 20:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('care_point', '0009_auto_20181221_2105'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ward',
            old_name='name',
            new_name='first_name',
        ),
        migrations.RenameField(
            model_name='ward',
            old_name='sname',
            new_name='last_name',
        ),
        migrations.AlterField(
            model_name='contract',
            name='date_from',
            field=models.DateField(blank=True, default='2018-12-22', null=True),
        ),
        migrations.AlterField(
            model_name='contract',
            name='date_to',
            field=models.DateField(blank=True, default='2018-12-22', null=True),
        ),
        migrations.AlterField(
            model_name='ward',
            name='pesel',
            field=models.DecimalField(decimal_places=0, max_digits=15, max_length=15),
        ),
        migrations.AlterField(
            model_name='worksheet',
            name='date',
            field=models.DateField(blank=True, default='2018-12-22', null=True),
        ),
    ]
