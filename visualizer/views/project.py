from django.shortcuts import render

from visualizer.models import Project


def index(request):
    projects = Project.objects.all()
    return render(request, 'project_list.html', {'projects': projects})
