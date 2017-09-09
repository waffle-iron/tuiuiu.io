# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-26 13:38
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tuiuiucore', '0032_add_bulk_delete_page_permission'),
        ('tests', '0016_auto_20170303_2340'),
    ]

    operations = [
        migrations.CreateModel(
            name='AlwaysShowInMenusPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='tuiuiucore.Page')),
            ],
            options={
                'abstract': False,
            },
            bases=('tuiuiucore.page',),
        ),
    ]
