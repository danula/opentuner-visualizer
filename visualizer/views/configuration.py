from django.http import HttpResponseRedirect

from visualizer.models import Project

__author__ = 'madawa'

from django import forms
import pickle
import zlib
from copy import deepcopy
from django.shortcuts import render
from django.shortcuts import render_to_response
from opentuner.search.manipulator import EnumParameter, NumericParameter
from opentuner.resultsdb.models import Configuration
from opentuner.resultsdb.connect import connect
from visualizer.views.custom_run import custom_run
import constants
manipulator = None
fields = {}

class ConfigurationForm(forms.Form):
    pass


def unpickle_data(data):
    try:
        data = zlib.decompress(data)
    except:
        pass
    return pickle.loads(data)

def read_manipulator():
    global manipulator, fields
    manipulator = constants.get_manipulator()
    fields = {}
    print(manipulator)
    i = 0
    for p in manipulator.params:
        if isinstance(p, NumericParameter):
            fields[p.name] = forms.IntegerField(p.max_value, p.min_value,
                                                widget=forms.NumberInput(attrs={'class': 'form-control'}))
        elif isinstance(p, EnumParameter):
            fields[p.name] = forms.ChoiceField(
                choices=tuple([(p.options[i], p.options[i]) for i in range(len(p.options))]),
                widget=forms.Select(attrs={'class': 'form-control'})
            )


def create_form(cfg):
    form = ConfigurationForm()
    form.fields.update(deepcopy(fields))
    for p in manipulator.params:
        form.fields[p.name].initial = p._get(cfg)
    return form


def index(request, project_id, config_id):
    project = Project.objects.get(pk=project_id)
    if request.method == 'POST':
        return configuration_edit(request, project_id)
    else:
        read_manipulator()
        engine, session = connect("sqlite:///" + constants.get_database_url())
        session = session()
        configuration = session.query(Configuration).filter_by(id=config_id).one()
        data = configuration.data.copy()
        form = create_form(data)
        return render(request, "configuration.html", {'form': form, 'project': project})


def configuration_edit(request, project_id):
    data = request.POST.dict()
    cfg = {}
    is_new_tuning_run = False
    if data["isNewTuningRun"] == "true":
        is_new_tuning_run = True

    for p in manipulator.params:
        if isinstance(p, NumericParameter):
            cfg[p.name] = int(data[p.name])
        elif isinstance(p, EnumParameter):
            cfg[p.name] = data[p.name]

    custom_run(cfg, is_new_tuning_run)
    return HttpResponseRedirect('/plots/'+project_id)
    # return render_to_response("plot.html")
