__author__ = 'kasun'

from django.shortcuts import render
from django.utils.safestring import mark_safe


def index(request):
    return render(request, 'index.html')
