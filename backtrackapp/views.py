from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic

from .models import Project

# Create your views here.
class IndexView(generic.ListView):
    template_name = 'backtrackapp/index.html'
    context_object_name = 'projects'

    def get_queryset(self):
        return Project.objects.all()
