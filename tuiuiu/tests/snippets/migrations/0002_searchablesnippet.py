# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

import tuiuiu.tuiuiusearch.index


class Migration(migrations.Migration):

    dependencies = [
        ('snippetstests', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SearchableSnippet',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('text', models.CharField(max_length=255)),
            ],
            bases=(tuiuiu.tuiuiusearch.index.Indexed, models.Model),
        ),
    ]
