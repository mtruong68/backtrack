from django.urls import path

from . import views

app_name = 'backtrack'
urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),

    path('', views.IndexView.as_view(), name='index'),

    path('newproject/', views.NewProjectView.as_view(), name="new_project"),

    path('<int:pk>/productbacklog/', views.ProductBacklogView.as_view(), name="project_pb"),
    path('<int:pk>/newPBI/', views.NewPBIView.as_view(), name="new_PBI"),
    path('<int:pk>/modifyPBI/', views.ModifyPBIView.as_view(), name="modify_PBI"),

    path('<int:pk>/sprintbacklog/', views.SprintBacklogView.as_view(), name="project_sb"),
    path('<int:pk>/newsprint/', views.NewTaskView.as_view(), name="new_sprint"),
    path('<int:pk>/newtask/', views.NewTaskView.as_view(), name="new_task"),
    path('<int:pk>/modifytask/', views.ModifyTaskView.as_view(), name="modify_task"),
]
