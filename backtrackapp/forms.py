from django import forms
from .models import Project, ProductBacklogItem, Task

class NewProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = '__all__'

class NewPBIForm(forms.ModelForm):
    class Meta:
        model = ProductBacklogItem
        exclude = ['project']

class NewTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = '__all__'
