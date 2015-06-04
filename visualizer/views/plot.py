from django.shortcuts import render


def index(request):
    return render(request, 'plot.html', {'foo':'test'})
