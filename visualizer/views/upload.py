from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST

__author__ = 'madawa'


@ensure_csrf_cookie
def index(request):
    return render(request, 'upload.html')


def save_file(f, fname):
    global location
    if fname is 'database':
        location = '/configuration_files/database.db'
    elif fname is 'manipulator':
        location = '/configuration_files/manipulator'
    try:
        with open(location, 'wb+') as destination:
            print(location)
            for chunk in f.chunks():
                print(chunk)
                destination.write(chunk)
        return True
    except Exception:
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