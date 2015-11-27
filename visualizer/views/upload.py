from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
import os
import constants
from os import path
from visualizer import utils

__author__ = 'madawa'


@ensure_csrf_cookie
def index(request):
    return render(request, 'upload.html')


def save_file(f, config_type):
    location = 'configuration_files/'
    try:
        if not path.exists(path.dirname(location)):
            os.makedirs(path.dirname(location))
        with open('configuration_files/'+f.name, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)
        if config_type == 'database':
            constants.database_url = location+f.name
        elif config_type == 'manipulator':
            constants.manipulator_url = location+f.name
        return True
    except EnvironmentError:
        return False

@require_POST
def upload_files(request):
    global a, b
    if request.method == 'POST':
        database = request.FILES['database']
        manipulator = request.FILES['manipulator']
        if database is not None:
            a = save_file(database, 'database')
        if manipulator is not None:
            b = save_file(manipulator, 'manipulator')

    if a is True and b is True:
        return HttpResponse("success")
    else:
        return HttpResponse("error")