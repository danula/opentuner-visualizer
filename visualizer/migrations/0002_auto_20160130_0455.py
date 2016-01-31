# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('visualizer', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='manipulator',
            field=models.FileField(default='', upload_to=b'manipulator/'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='analysis',
            name='result_doc',
            field=models.FileField(null=True, upload_to=b''),
            preserve_default=True,
        ),
    ]
