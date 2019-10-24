from django import forms
from .models import Project, ProductBacklogItem, Task

class NewProjectForm(forms.ModelForm):
    class Meta:
        model = Project
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
        fields = '__all__'
