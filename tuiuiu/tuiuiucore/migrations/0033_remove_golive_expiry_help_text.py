# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-31 14:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tuiuiucore', '0032_add_bulk_delete_page_permission'),
    ]

    operations = [
        migrations.AlterField(
            model_name='page',
            name='expire_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='expiry date/time'),
        ),
        migrations.AlterField(
            model_name='page',
            name='go_live_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='go live date/time'),
        ),
    ]
