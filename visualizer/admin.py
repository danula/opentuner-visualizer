from django.contrib.auth.models import User, Group

from django.contrib import admin

from visualizer.forms import AnalysisForm
from visualizer.models import Project
from visualizer.models import Analysis


class AnalysisAdmin(admin.ModelAdmin):
    form = AnalysisForm

admin.site.register(Project)
admin.site.register(Analysis, AnalysisAdmin)

admin.site.unregister(User)
admin.site.unregister(Group)
