# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tuiuiuembeds', '0002_add_verbose_names'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='embed',
            options={'verbose_name': 'embed'},
        ),
    ]