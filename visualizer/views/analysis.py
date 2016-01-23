from django.shortcuts import render
from django.views.decorators.http import require_POST


__author__ = 'madawa'


def create(request):
    return render(request, 'analysis.html')


@require_POST
def store(request):
    return request
