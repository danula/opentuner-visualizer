from django.views.decorators.http import require_POST, require_GET
from django.shortcuts import render
from django.forms import ModelForm
from visualizer.models import Project


class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'database', 'tuning_data']


@require_GET
def index(request):
    projects = Project.objects.all()
    return render(request, 'project_list.html', {'projects': projects})


@require_GET
def show(request):
    return render(request, 'project_list.html')


@require_GET
def destroy(request):
    return render(request, 'project_list.html')
