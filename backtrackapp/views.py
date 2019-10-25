from django.views import generic
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from .forms import NewProjectForm, NewPBIForm, NewTaskForm
from .models import Project, ProductBacklogItem, Sprint, Task

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

#Views handling the client accessing the Product Backlog
#Maybe make separate view for just looking at the product backlog
class ProjectPBView(generic.CreateView):
    #need to sort pbi by priority and show in order of priorty
    def get(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        context = {'form': NewPBIForm(initial={'project': project}),
        'project': project}
        return render(request, 'backtrackapp/projectpbview.html', context)

    def post(self, request, pk):
        if 'addToSprint' in self.request.POST:
            return self.addToSprint(request, pk)
        if 'createNewPBI' in self.request.POST:
            return self.createNewPBI(request, pk)
        if 'deletePBI' in self.request.POST:
            return self.deletePBI(request, pk)
        if 'splitPBI' in self.request.POST:
            return self.splitPBI(request, pk)
        else:
            #this is a stub method and needs to be changed
            print(form.errors)
            return HttpResponse("Did not work.")

    def addToSprint(self, request, pk):
        latestSprint = Sprint.objects.latest('start_date')
        pbi_id = request.POST.get('pbi')
        pbi = get_object_or_404(ProductBacklogItem, pk=pbi_id)
        pbi.sprint = latestSprint
        pbi.save()
        return HttpResponseRedirect(reverse('backtrack:project_pb', args=(pk,)))

    def deletePBI(self, request, pk):
        pbi_id = request.POST.get('pbi')
        ProductBacklogItem.objects.get(pk=pbi_id).delete()
        return HttpResponseRedirect(reverse('backtrack:project_pb', args=(pk,)))

    def createNewPBI(self, request, pk):
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

    def splitPBI(self, request, pk):
        proj = get_object_or_404(Project, pk=pk)
        num = request.POST.get('numOfChildPBI')
        pbi_id = request.POST.get('pbi')
        pbi = ProductBacklogItem.objects.get(pk=pbi_id)
        i = 1
        while (i <= int(num)):
            ProductBacklogItem.objects.create(name = pbi.name + "." + str(i), desc = pbi.desc, priority = pbi.priority, storypoints = pbi.storypoints, status = pbi.status, project = proj)
            i = i + 1
        ProductBacklogItem.objects.get(pk=pbi_id).delete()
        #redirect back to product backlog view
        return HttpResponseRedirect(reverse('backtrack:project_pb', args=(pk,)))

#Views handling the client accessing the Sprint Backlog
#NOTE THIS IS NOT YET "COMPLETE" FORMS MUST BE INCLUDED
class SprintBacklogView(generic.DetailView):
    def get(self, request, pk):
        sprint = get_object_or_404(Sprint, pk=pk)
        return render(request, 'backtrackapp/projectsbview.html', {'sprint':sprint})

    def post(self, pk, request):
        if 'createNewTask' in self.request.POST:
            return self.createNewTask(pk, request)
        else:
            #this is a stub method and needs to be changed
            print(form.errors)
            return HttpResponse("Did not work.")

    #METHOD NOT FINISHED YET
    def createNewTask(self, request, pk):
        pbi = get_object_or_404(ProductBacklogItem, pk=pk)
        form = NewTaskForm(request.POST, initial={"pbi":pbi})
        if form.is_valid():
            newTask = form.save(commit=False)
            newTask.pbi = pbi
            newTask.save()
            return HttpResponseRedirect(reverse('backtrack:project_sb', args=(pk,)))
        else:
            #this is a stub method and needs to be changed
            print(form.errors)
            return HttpResponse("Did not work.")










#Views handling the client accessing the Product Backlog
#Maybe make separate view for just looking at the product backlog
class modifyPBI(generic.CreateView):
    #need to sort pbi by priority and show in order of priorty
    def get(self, request, pk):
        pbi = get_object_or_404(ProductBacklogItem, pk=pk)
        context = {'form': NewPBIForm(initial={'pbi': pbi}),
        'pbi': pbi}
        return render(request, 'backtrackapp/modifyPBI.html', context)

    def post(self, request, pk):
        if 'savePBI' in self.request.POST:
            return self.savePBI(request, pk)
        else:
            #this is a stub method and needs to be changed
            print(form.errors)
            return HttpResponse("Did not work.")

    def savePBI(self, request, pk):
        pbi_id = request.POST.get('pbi')
        pbi = get_object_or_404(ProductBacklogItem, pk=pbi_id)
        pbi.name = request.POST.get('newName')
        pbi.desc = request.POST.get('newDesc')
        pbi.priority = request.POST.get('newPri')
        pbi.storypoints = request.POST.get('newSto')
        pbi.status = request.POST.get('newSta')
        pbi.save()
        return HttpResponseRedirect(reverse('backtrack:modifyPBI', args=(pk,)))
