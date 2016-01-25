from django.db import models

from visualizer import settings


class Project(models.Model):
    app_label = 'visualizer'
    name = models.CharField(max_length=50)
    database = models.FileField(upload_to='databases/', null=True)
    tuning_data = models.FileField(upload_to='tuning_data/', null=True)


class Analysis(models.Model):
    app_label = 'visualizer'
    name = models.CharField(max_length=50)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    result_doc = models.FilePathField(path=settings.BASE_DIR + '/media/results/')
