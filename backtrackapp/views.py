from django.views import generic
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from .forms import NewProjectForm, NewPBIForm, NewTaskForm
from .models import Project, ProductBacklogItem

#Index and New Project View are currently the same... delete one
def IndexView(request):
    projects = Project.objects.all()
    form = NewProjectForm()

    if request.method == 'POST':
        form = NewProjectForm(request.POST)
        if form.is_valid():
            newProject = form.save()
            newProject.save()
            #use backtrack instead of backtrackapp bc of app name specified in urls
            return HttpResponseRedirect(reverse('backtrack:index'))
    else:
        form = NewProjectForm()

    return render(request,
    'backtrackapp/index.html',
    {'form': form,
    'projects': projects})

class NewProjectView(generic.CreateView):
    def get(self, request):
        context = {'form': NewProjectForm()}
        return render(request, 'backtrackapp/index.html', context)

    def post(self, request):
        form = NewProjectForm(request.POST)
        projects = Project.objects.all()
        if form.is_valid():
            newProject = form.save()
            newProject.save()
            return HttpResponseRedirect(reverse('backtrack:index'))

        return render(request,
        'backtrackapp/index.html',
        {'projects': projects,'form': form})

#Change classname to NewPBIView?
#Maybe make separate view for just looking at the product backlog
class ProjectPBView(generic.CreateView):
    def get(self, request, pk):
        #sort project pbi by priority then return
        project = get_object_or_404(Project, pk=pk)
        context = {'form': NewPBIForm(initial={'project': project}),
        'project': project}
        return render(request, 'backtrackapp/projectpbview.html', context)

    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        form = NewPBIForm(request.POST, initial={'project': project})
        if form.is_valid():
            newPBI = form.save(commit=False)
            newPBI.project = project
            newPBI.save()
            #redirect back to product backlog view
            return HttpResponseRedirect(reverse('backtrack:project_pb', args=(pk,)))
        else:
            #this is a stub method and needs to be changed
            print(form.errors)
            return HttpResponse("Did not work.")

        return render(request,
        'backtrackapp/projectpbview.html',
        {'project': project,'form': form})

#class NewTaskView(generic.CreateView):
