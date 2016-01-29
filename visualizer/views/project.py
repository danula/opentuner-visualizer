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
def create(request):
    form = ProjectForm()
    return render(request, 'project_create.html', {'form': form})


@require_GET
def show(request, project_id):
    project = Project.objects.get(pk=project_id)
    return render(request, 'project.html', {'project': project})


@require_POST
def store(request):
    new_project = ProjectForm(request.POST, request.FILES)
    new_project.save()
    return render(request, 'project_list.html')


@require_GET
def destroy(request, project_id):
    project = Project.objects.get(pk=project_id)
    project.delete()
    return render(request, 'project_list.html')
