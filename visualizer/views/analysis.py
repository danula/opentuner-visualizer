from datetime import datetime

from django.http.response import HttpResponseRedirect
from django import forms
from django.forms import ModelForm
from django.shortcuts import render
from django.views.decorators.http import require_POST, require_GET

from visualizer import utils
from visualizer.models import Project, Analysis


class CustomUserChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.get_name()


class AnalysisForm(ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'id': 'name', 'class': 'form-control'}))
    project = CustomUserChoiceField(queryset=Project.objects.all(),
                                    widget=forms.Select(attrs={
                                        'id': 'project',
                                        'class': 'form-control'
                                    }))
    method = forms.ChoiceField(choices=(
        ('remove_param', 'Remove Parameters'), ('compare_bin', 'Compare Binaries'), ('random_forest', 'Random Forest'),
        ('relief', 'Relief')))

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
    analysis.status = 'created'
    analysis.tuning_data.name = utils.generate_tuning_data(project.database.name, project.manipulator.name,
                                                           project.name, analysis.name)

    analysis.save()

    redirect_url = '/project/' + str(project.pk)

    return HttpResponseRedirect(redirect_url)


@require_GET
def show(request, analysis_id):
    analysis = Analysis.objects.get(pk=analysis_id)
    return render(request, 'analysis.html', {'analysis': analysis})


@require_GET
def destroy(analysis_id):
    """
    Removes the given Analysis from the database
    :param analysis_id: Index of the Analysis to delete
    :return: Redirects to project view
    """
    analysis = Analysis.object.get(pk=analysis_id)
    analysis.delete()
    redirect_url = 'project/' + str(analysis.project.pk)
    return HttpResponseRedirect(redirect_url)


def runscript(input, output):
    import subprocess
    try:
        subprocess.check_output(["Rscript", "rscripts/randomForest.r", input, output])
    except subprocess.CalledProcessError:
        pass
