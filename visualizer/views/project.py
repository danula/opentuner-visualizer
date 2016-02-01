import os

from django.views.decorators.http import require_POST, require_GET
from django.shortcuts import render
from django.forms import ModelForm, TextInput, FileInput
from visualizer.models import Project
import visualizer.utils as utils


class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'database', 'manipulator']

    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget = TextInput(attrs={
            'id': 'name',
            'class': 'form-control',
            'placeholder': 'Project Name'})
        self.fields['database'].widget = FileInput(attrs={'id': 'database'})
        self.fields['manipulator'].widget = FileInput(attrs={'id': 'manipulator'})


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
    project = Project()
    project_name = request.POST['name']
    database = request.FILES['database']
    manipulator = request.FILES['manipulator']

    project.name = project_name

    if database is not None:
        project.database.name = utils.save_file(database, os.path.join('databases', project_name))

    if manipulator is not None:
        project.manipulator.name = utils.save_file(manipulator, os.path.join('manipulator', project_name))

    project.save()
    return render(request, 'project_list.html')


@require_GET
def destroy(request, project_id):
    project = Project.objects.get(pk=project_id)
    project.delete()
    return render(request, 'project_list.html')
