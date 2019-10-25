from django.urls import path

from . import views

app_name = 'backtrack'
urlpatterns = [
    path('', views.IndexView, name='index'),

    path('newproject', views.NewProjectView.as_view(), name="new_project"),

    path('<int:pk>/productbacklog/', views.ProjectPBView.as_view(), name="project_pb"),

    path('<int:pk>/modifyPBI/', views.modifyPBI.as_view(), name="modifyPBI"),

    path('<int:pk>/sprintbacklog/', views.SprintBacklogView.as_view(), name="project_sb"),
]
