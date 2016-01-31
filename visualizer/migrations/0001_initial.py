# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Analysis',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('method', models.CharField(max_length=20)),
                ('status', models.CharField(default=b'created', max_length=10, null=True)),
                ('result_doc', models.FileField(null=True, upload_to=b'results/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('database', models.FileField(null=True, upload_to=b'databases/')),
                ('tuning_data', models.FileField(null=True, upload_to=b'tuning_data/')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='analysis',
            name='project',
            field=models.ForeignKey(to='visualizer.Project'),
            preserve_default=True,
        ),
    ]
