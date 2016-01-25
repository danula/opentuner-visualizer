from django.views.decorators.http import require_POST

from django.shortcuts import render
from django.forms import ModelForm

from visualizer.models import Project


class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'database', 'tuning_data']


def index(request):
    projects = Project.objects.all()
    return render(request, 'project_list.html', {'projects': projects})


def create(request):
    form = ProjectForm()
    return render(request, 'project_create.html', {'form': form})


def show(request):
    return render(request, 'project_list.html')


@require_POST
def store(request):
    new_project = ProjectForm(request.POST, request.FILES)
    new_project.save()
    return render(request, 'project_list.html')


def destroy(request):
    return render(request, 'project_list.html')
