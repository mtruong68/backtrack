from django import forms
from .models import Project, ProductBacklogItem, Task, User, ProjectTeam

from django.contrib.auth.forms import UserCreationForm, UserChangeForm

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'name', 'isManager')
        exclude = ['avaliable','current_project']

class ProjectTeamForm(forms.ModelForm):
    class Meta:
        model = ProjectTeam
        prefix = "teamForm"
        exclude = ['project','product_owner']
        labels = {
        "teamName": "Team Name",
        "scrum_master": "Scrum Master",
        "dev_team": "Development Team"
        }

class NewProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        prefix = "projectForm"
        fields = '__all__'
        labels = {
        "desc": "Description",
        "endDate": "End Date",
        "startDate": "Start Date"
        }

class NewPBIForm(forms.ModelForm):
    class Meta:
        model = ProductBacklogItem
        exclude = ['project', 'sprint', 'status']
        labels = {
        "desc": "Description",
        "storypoints": "Story Points"
        }

class NewTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        exclude = ['pbi', 'status', 'assignment']
        labels = {
        "desc": "Description",
        "assignment": "Assigned To"
        }
