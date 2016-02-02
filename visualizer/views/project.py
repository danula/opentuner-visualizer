import os

from django.forms import ModelForm, TextInput, FileInput, ValidationError
from django.http import HttpResponseRedirect
from django.shortcuts import render, render_to_response
from django.views.decorators.http import require_POST, require_GET

import visualizer.utils as utils
from visualizer.models import Project


class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'database', 'manipulator', 'database_url']

    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget = TextInput(attrs={
            'id': 'name',
            'class': 'form-control',
            'placeholder': 'Project Name',
            'required': 'required'})
        self.fields['database'].widget = FileInput(attrs={'id': 'database'})
        self.fields['manipulator'].widget = FileInput(attrs={
            'id': 'manipulator',
            'required': 'required'})
        self.fields['database_url'].widget = TextInput(attrs={
            'id': 'manipulator',
            'class': 'form-control',
            'placeholder': 'Database URL'})

    def clean(self):
        cleaned_data = super(ProjectForm, self).clean()
        if cleaned_data.get("database") is None and not cleaned_data.get("database_url"):
            raise ValidationError('Either database or a url to a database should be present.')


@require_GET
def index(request):
    projects = Project.objects.all()
    return render(request, 'project_list.html', {'projects': projects})


def create(request):
    form = None
    if request.method == 'GET':
        form = ProjectForm()
    if request.method == 'POST':
        project = Project()

        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            database = None
            project.name = request.POST['name']
            if form.cleaned_data.get('database'):
                database = request.FILES['database']
            if form.cleaned_data.get('database_url'):
                project.database_url = form.cleaned_data.get('database_url')
            manipulator = request.FILES['manipulator']

            if database is not None:
                project.database.name = utils.save_file(database, os.path.join('databases', project.name))

            if manipulator is not None:
                project.manipulator.name = utils.save_file(manipulator, os.path.join('manipulator', project.name))

            project.save()
            return HttpResponseRedirect('/project/list/')
    return render(request, 'project_create.html', {'form': form})


@require_GET
def show(request, project_id):
    project = Project.objects.get(pk=project_id)
    import constants
    if project.database_url:
        constants.database_url = project.database_url
    else:
        constants.database_url = project.database.name
    constants.manipulator_url = project.manipulator.name
    return HttpResponseRedirect('/plot')


@require_GET
def destroy(request, project_id):
    project = Project.objects.get(pk=project_id)
    project.delete()
    return render(request, 'project_list.html')
