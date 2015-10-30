from collections import OrderedDict

__author__ = 'madawa'

from django import forms
from  opentuner.search.manipulator import IntegerParameter, EnumParameter
import constants
import pickle
import zlib
from copy import deepcopy


class ConfigurationForm(forms.Form):
    pass


def unpickle_data(data):
    try:
        data = zlib.decompress(data)
    except:
        pass
    return pickle.loads(data)

with open(constants.manipulator_url, "r") as f1:
    manipulator = unpickle_data(f1.read())
    fields = {}
    for p in manipulator.params:
        if isinstance(p, IntegerParameter):
            fields[p.name] = forms.IntegerField(p.max_value. p.min_value)
        elif isinstance(p, EnumParameter):
            fields[p.name] = forms.ChoiceField(tuple(p.options))

def create_form(cfg):
    form = ConfigurationForm()
    form.fields.update(deepcopy(fields))
    for p in manipulator.params:
        form.declared_fields[p.name].initial = p.get_value(cfg)
    return form


