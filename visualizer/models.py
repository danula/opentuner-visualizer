from django.db import models


class Project(models.Model):
    app_label = 'visualizer'
    name = models.CharField(max_length=50)
    database = models.FileField(upload_to='databases/', null=True, blank=True)
    manipulator = models.FileField(upload_to='manipulator/', null=True)
    database_url = models.TextField(null=True, blank=True)

    def get_name(self):
        return self.name


class Analysis(models.Model):
    app_label = 'visualizer'
    name = models.CharField(max_length=50)
    method = models.CharField(max_length=20)
    status = models.CharField(max_length=10, default='created', null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    tuning_data = models.FileField(upload_to='tuning_data/', null=True, blank=True)
    result_doc = models.FileField(upload_to='result_data/', null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.name
