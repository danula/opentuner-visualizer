from django.db import models


class Project(models.Model):
    app_label = 'visualizer'
    name = models.CharField(max_length=50)
    database = models.FileField(upload_to='databases/', null=True)
    tuning_data = models.FileField(upload_to='tuning_data/', null=True)

    def get_name(self):
        return self.name


class Analysis(models.Model):
    app_label = 'visualizer'
    name = models.CharField(max_length=50)
    method = models.CharField(max_length=20)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    result_doc = models.FileField(upload_to='results/', null=True)

    def __unicode__(self):
        return self.name
