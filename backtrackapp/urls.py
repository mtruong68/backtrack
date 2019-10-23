from django.urls import path

from . import views

app_name = 'backtrack'
urlpatterns = [
    path('', views.IndexView, name='index'),
    path('newproject', views.newProjectView.as_view(), name="newProject"),
]
