# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import modelcluster.fields
import tuiuiu.tuiuiucore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('tuiuiucore', '0028_merge'),
        ('tests', '0005_customrichblockfieldpage_customrichtextfieldpage_defaultrichblockfieldpage_defaultrichtextfieldpage'),
    ]

    operations = [
        migrations.CreateModel(
            name='SectionedRichTextPage',
            fields=[
                ('page_ptr', models.OneToOneField(parent_link=True, to='tuiuiucore.Page', serialize=False, auto_created=True, primary_key=True, on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
            },
            bases=('tuiuiucore.page',),
        ),
        migrations.CreateModel(
            name='SectionedRichTextPageSection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('sort_order', models.IntegerField(editable=False, null=True, blank=True)),
                ('body', tuiuiu.tuiuiucore.fields.RichTextField()),
                ('page', modelcluster.fields.ParentalKey(related_name='sections', to='tests.SectionedRichTextPage', on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
    ]
