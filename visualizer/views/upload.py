from django.shortcuts import render

__author__ = 'madawa'


def index(request):
    return render(request, 'upload.html')