from django import forms
from .models import Project

class NameForm(forms.Form):
    your_name = forms.CharField(label='Your name', max_length=100)

class NewProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = '__all__'
