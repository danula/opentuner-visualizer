import csv
import os

from datetime import datetime

import math
from django import forms
from django.forms import ModelForm
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.http import require_POST, require_GET

from visualizer import utils
from visualizer import settings
from visualizer.models import Project, Analysis


class CustomUserChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.get_name()


class AnalysisForm(ModelForm):
    name = forms.CharField(
            widget=forms.TextInput(attrs={'id': 'name', 'class': 'form-control', 'required': 'required'}))
    project = CustomUserChoiceField(queryset=Project.objects.all(),
                                    widget=forms.Select(attrs={
                                        'id': 'project',
                                        'class': 'form-control'
                                    }))
    method = forms.ChoiceField(choices=(('random_forest', 'Random Forest'), ('relief', 'Relief')))

    class Meta:
        model = Analysis
        exclude = ['result_doc', 'status', 'created_at', 'tuning_data']


@require_GET
def create(request):
    """
    Creates the Analysis creation form
    :param request: GET request from the web application
    :return: Analysis creation form
    """
    form = AnalysisForm()
    return render(request, 'analysis_create.html', {'form': form})


@require_POST
def store(request):
    """
    Stores the Analysis in the database
    :param request: POST request from the form
    :return: redirect to the project view
    """
    analysis = Analysis()
    project = Project.objects.get(pk=request.POST['project'])
    analysis.name = request.POST['name']
    analysis.created_at = datetime.now()
    analysis.method = request.POST['method']
    analysis.project = project
    analysis.status = 'incomplete'
    analysis.tuning_data.name = utils.generate_tuning_data(project.database.name, project.manipulator.name,
                                                           project.name, analysis.name)

    analysis.save()
    out_path = os.path.join('result_data', project.name, analysis.name, 'result.csv')
    if not os.path.exists(os.path.dirname(out_path)):
        os.makedirs(os.path.dirname(out_path))
    method = 'randomForest.r'

    if analysis.method is 'relief':
        method = 'relief.r'

    runscript(analysis.tuning_data.name, method, out_path, analysis.pk)
    redirect_url = '/project/' + str(project.pk)

    return HttpResponseRedirect(redirect_url)


@require_GET
def show(request, analysis_id):
    analysis = Analysis.objects.get(pk=analysis_id)
    project = analysis.project
    rows = []
    with open(analysis.result_doc.name, 'rb') as f:
        l = csv.reader(f, delimiter=',', quotechar='|')
        next(l, None)
        for row in l:
            rows.append([row[0].replace("\"", ""), float(row[1])])
    rows.sort(key=lambda x: x[0])
    s = sum([row[1] for row in rows])
    m = min([row[1] for row in rows])
    json_data = [{'Params': row[0], 'Importance': (row[1] - m) * 100.0 / s} for row in rows]
    rows.sort(key=lambda x: -x[1])
    top_params = [{'Params': row[0], 'Importance': math.floor((row[1] - m) * 10000.0 / s) / 100.0} for row in rows[:10]]

    return render(request, 'analysis.html',
                  {'analysis': analysis, 'json': json_data, 'top': top_params, 'project': project})


@require_GET
def destroy(request, analysis_id):
    """
    Removes the given Analysis from the database
    :param analysis_id: Index of the Analysis to delete
    :return: Redirects to project view
    """
    analysis = Analysis.objects.get(pk=analysis_id)
    analysis.delete()
    return HttpResponseRedirect('/project/list/')


def runscript(tuning_data, method, out_path, analysis):
    import subprocess

    database = os.path.join(settings.BASE_DIR, 'visualizer.sqlite3')
    subprocess.Popen(
            "Rscript visualizer/rscripts/" + method + " '%s' '%s' '%s' '%s'" % (
                tuning_data, out_path, database, analysis),
            shell=True, stdin=None, stdout=None, stderr=None, close_fds=True
    )
