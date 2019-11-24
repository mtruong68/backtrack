from django import forms
from .models import Project, ProductBacklogItem, Task, User, ProjectTeam

from django.contrib.auth.forms import UserCreationForm, UserChangeForm

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'name', 'role')
        exclude = ['avaliable','current_project']

class ProjectTeamForm(forms.ModelForm):
    class Meta:
        model = ProjectTeam
        prefix = "teamForm"
        exclude = ['project','product_owner']

class NewProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        prefix = "projectForm"
        fields = '__all__'
        labels = {
        "desc": "Description"
        }

class NewPBIForm(forms.ModelForm):
    class Meta:
        model = ProductBacklogItem
        exclude = ['project', 'sprint']
        labels = {
        "desc": "Description",
        "storypoints": "Story Points"
        }

class NewTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        exclude = ['pbi']
        labels = {
        "desc": "Description",
        "assignment": "Assigned To"
        }
