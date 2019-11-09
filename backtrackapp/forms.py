from django import forms
from .models import Project, ProductBacklogItem, Task, User, ProjectTeam, Sprint

from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from durationwidget.widgets import TimeDurationWidget

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'name')

class ProjectTeamForm(forms.ModelForm):
    class Meta:
        model = ProjectTeam
        prefix = "teamForm"
        exclude = ['project','product_owner']

class NewProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        prefix = "projectForm"
        exclude = ['end_date']
        labels = {
        "desc": "Description"
        }

class NewSprintForm(forms.ModelForm):
    class Meta:
        model = Sprint
        fields = ['interval', ]
        widgets = {
            'interval': TimeDurationWidget(),
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

class DateForm(forms.Form):
    date = forms.DateTimeField(input_formats=['%d/%m/%Y %H:%M'])
