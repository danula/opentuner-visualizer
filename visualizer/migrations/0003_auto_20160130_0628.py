# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('visualizer', '0002_auto_20160130_0455'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='manipulator',
            field=models.FileField(null=True, upload_to=b'manipulator/'),
            preserve_default=True,
        ),
    ]
