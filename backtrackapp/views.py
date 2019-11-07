from django.views import generic
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy

from .forms import NewProjectForm, NewPBIForm, NewTaskForm, CustomUserCreationForm
from .models import Project, ProductBacklogItem, Sprint, User, Task


class SignUpView(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'

#Index and New Project View are currently the same... delete one
#We need to create different index views based on the type of role the user has

#if no current project or is the product owner, show the product backlog first
#if a developer, show the task view
#do the manager stuff later

def IndexView(request):
    user = request.user
    if user.is_authenticated:
        projects = Project.objects.all()
        form = NewProjectForm()

        if request.method == 'POST':
            form1 = NewProjectForm(request.POST, prefix="projectForm")
            form2 = ProjectTeamForm(request.POST, prefix="teamForm")
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
    else:
        return HttpResponseRedirect(reverse('login'))

class ProjectView(generic.View):
    def get(self, request):
        user = request.user
        if user.is_authenticated:
            context = {'form': NewProjectForm()}
            return render(request, 'backtrackapp/index.html', context)
        else:
            return HttpResponseRedirect(reverse('login'))

    def post(self, request):
        form = NewProjectForm(request.POST)
        projects = Project.objects.all()
        if form.is_valid():
            newProject = form.save()
            newProject.save()
            return HttpResponseRedirect(reverse('index'))

        return render(request,
        'backtrackapp/index.html',
        {'projects': projects,'form': form})

#Views handling the client accessing the Product Backlog
#Maybe make separate view for just looking at the product backlog
class ProjectPBView(generic.View):
    def get(self, request, pk):
        user = request.user
        if user.is_authenticated:
            project = get_object_or_404(Project, pk=pk)

            #sort pbi by priority and then calculate cumulative point total
            pbi_cum_points_list = []
            pbi_set = project.productbacklogitem_set.all().order_by('priority')
            total_sum = 0
            for pbi in pbi_set:
                pbi_cum_points_set = {}
                pbi_cum_points_set["pbi"] = pbi
                total_sum += pbi.storypoints
                pbi_cum_points_set["cum_points"] = total_sum
                pbi_cum_points_list.append(pbi_cum_points_set)

            #get the latest sprint and show the sprint backlog of that sprint
            sprints = project.sprint_set.all()
            if len(sprints) > 0:
                latestSprint = sprints.latest('start_date')
            else:
                latestSprint = None

            context = {'form': NewPBIForm(initial={'project': project}),
            'project': project, 'latestSprint': latestSprint,
            'pbi_cum_points_list': pbi_cum_points_list}

            return render(request, 'backtrackapp/projectpbview.html', context)
        else:
            return HttpResponseRedirect(reverse('login'))


    def post(self, request, pk):
        if 'addToSprint' in self.request.POST:
            return self.addToSprint(request, pk)
        if 'createNewPBI' in self.request.POST:
            return self.createNewPBI(request, pk)
        if 'deletePBI' in self.request.POST:
            return self.deletePBI(request, pk)
        if 'modifyPBI' in self.request.POST:
            pbi_id = request.POST.get('pbi')
            return HttpResponseRedirect(reverse('backtrack:modifyPBI', args=(pbi_id,)))
        else:
            #this is a stub method and needs to be changed
            print(form.errors)
            return HttpResponse("Did not work.")

    def addToSprint(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        sprints = project.sprint_set.all()
        latestSprint = sprints.latest('start_date')
        pbi_id = request.POST.get('pbi')
        pbi = get_object_or_404(ProductBacklogItem, pk=pbi_id)
        pbi.sprint = latestSprint
        pbi.save()
        return HttpResponseRedirect(reverse('backtrack:project_pb', args=(pk,)))

    def deletePBI(self, request, pk):
        pbi_id = request.POST.get('pbi')
        pbi = get_object_or_404(ProductBacklogItem, pk=pbi_id)
        self.updatePrioritiesDelete(pk, pbi.priority)
        pbi.delete()
        return HttpResponseRedirect(reverse('backtrack:project_pb', args=(pk,)))

    def createNewPBI(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        form = NewPBIForm(request.POST, initial={'project': project})
        if form.is_valid():
            newPBI = form.save(commit=False)
            newPBI.project = project
            if self.checkPriority(pk, request.POST.get('priority')) == False:
                return HttpResponse("Priority Out of Bounds")
            else:
                self.updatePriorities(request, pk, request.POST.get('priority'))
                newPBI.save()
                #redirect back to product backlog view
                return HttpResponseRedirect(reverse('backtrack:project_pb', args=(pk,)))
        else:
            #this is a stub method and needs to be changed
            print(form.errors)
            return HttpResponse("Did not work.")

    def checkPriority(self, pk, pri):
        proj = get_object_or_404(Project, pk=pk)
        max_priority = proj.productbacklogitem_set.all().count() + 1

        if int(pri) > max_priority or int(pri) <= 0:
            return False
        else:
            return True

    def updatePriorities(self, request, pk, pri):
        proj = get_object_or_404(Project, pk=pk)
        max_priority = proj.productbacklogitem_set.all().count() + 1
        newPri = int(pri)

        if newPri == max_priority:
            return
        else:
            pbis = proj.productbacklogitem_set.all()
            for i in pbis:
                if i.priority >= newPri:
                    temp = i.priority
                    i.priority = temp + 1
                    i.save()

    def updatePrioritiesDelete(self, pk, pri):
        proj = get_object_or_404(Project, pk=pk)
        pbis = proj.productbacklogitem_set.all()
        for pbi in pbis:
            if pbi.priority > pri:
                pbi.priority = pbi.priority - 1
                pbi.save()

#Views handling the client accessing the Sprint Backlog
class SprintBacklogView(generic.View):
    def get(self, request, pk):
        user = request.user
        if user.is_authenticated:
            sprint = get_object_or_404(Sprint, pk=pk)
            return render(request, 'backtrackapp/projectsbview.html', {'sprint':sprint})
        else:
            return HttpResponseRedirect(reverse('login'))


class NewTaskView(generic.View):
    def get(self, request, pk):
        user = request.user
        if user.is_authenticated:
            pbi = get_object_or_404(ProductBacklogItem, pk=pk)
            context = {'form': NewTaskForm(initial={'pbi': pbi}), 'pbi': pbi}
            return render(request, 'backtrackapp/newtask.html', context)
        else:
            return HttpResponseRedirect(reverse('login'))

    def post(self, request, pk):
        if 'modifyTask' in self.request.POST:
            return self.modifyTask(request, pk)
        if 'deleteTask' in self.request.POST:
            return self.deleteTask(request, pk)
        if 'addTask' in self.request.POST:
            return self.addTask(request, pk)
        else:
            #this is a stub method and needs to be changed
            print(form.errors)
            return HttpResponse("Did not work.")

    def deleteTask(self, request, pk):
        task_id = request.POST.get('task')
        Task.objects.get(pk=task_id).delete()
        return HttpResponseRedirect(reverse('backtrack:new_task', args=(pk,)))

    def modifyTask(self, request, pk):
        task_id = request.POST.get('task')
        return HttpResponseRedirect(reverse('backtrack:modify_task', args=(task_id,)))

    def addTask(self, request, pk):
        print(request.POST)
        pbi = get_object_or_404(ProductBacklogItem, pk=pk)
        form = NewTaskForm(request.POST, initial={"pbi":pbi})
        if form.is_valid():
            newTask = form.save(commit=False)
            assignGroup = request.POST.getlist('assignment')
            newTask.pbi = pbi
            newTask.save()
            for assign in assignGroup:
                newTask.assignment.add(User.objects.get(pk=assign))
                newTask.save()
            return HttpResponseRedirect(reverse('backtrack:new_task', args=(pk,)))
        else:
            #this is a stub method and needs to be changed
            print(form.errors)
            return HttpResponse("Did not work.")

class ModifyTaskView(generic.View):
    def get(self, request, pk):
        user = request.user
        if user.is_authenticated:
            task = get_object_or_404(Task, pk=pk)
            choices = [
                {'value': 'NS', 'status':'Not Started'},
                {'value': 'IP', 'status':'In Progress'},
                {'value': 'C', 'status': 'Complete'}
            ]

            for choice in choices:
                if choice['value'] == task.status:
                    choice['selected'] = "selected"

            availableUsers = User.objects.all().difference(task.assignment.all())

            context = {'task':task, 'choices': choices, 'availableUsers': availableUsers}

            return render(request, 'backtrackapp/modifytask.html', context)
        else:
            return HttpResponseRedirect(reverse('login'))

    def post(self, request, pk):
        if 'deleteUser' in self.request.POST:
            return self.deleteUserFromTask(request, pk)
        if 'modifyTask' in self.request.POST:
            return self.modifyTask(request, pk)

    #check to make sure some user is assigned
    def deleteUserFromTask(self, request, pk):
        user_id = request.POST.get('user')
        task = get_object_or_404(Task, pk=pk)
        task.assignment.remove(get_object_or_404(User, pk=user_id))
        return HttpResponseRedirect(reverse('backtrack:modify_task', args=(pk,)))

    #check to make sure that some user is assigned
    def modifyTask(self, request, pk):
        print(request.POST)
        task = get_object_or_404(Task, pk=pk)
        task.name = request.POST.get('name')
        task.desc = request.POST.get('desc')
        task.burndown = request.POST.get('burndown')
        task.status = request.POST.get('status')
        task.save()
        assignGroup = request.POST.getlist('assignment')
        if assignGroup != None:
            for assign in assignGroup:
                task.assignment.add(User.objects.get(pk=assign))
                task.save()
        return HttpResponseRedirect(reverse('backtrack:modify_task', args=(pk,)))

class ModifyPBI(generic.View):
    #need to sort pbi by priority and show in order of priority
    def get(self, request, pk):
        user = request.user
        if user.is_authenticated:
            pbi = get_object_or_404(ProductBacklogItem, pk=pk)
            context = {'form': NewPBIForm(initial={'pbi': pbi}),
            'pbi': pbi}
            return render(request, 'backtrackapp/modifyPBI.html', context)
        else:
            return HttpResponseRedirect(reverse('login'))

    def post(self, request, pk):
        if 'savePBI' in self.request.POST:
            return self.savePBI(request, pk)
        else:
            #this is a stub method and needs to be changed
            print(form.errors)
            return HttpResponse("Did not work.")

    def savePBI(self, request, pk):
        if self.checkPriority(request, pk) == False:
            return HttpResponse("Priority Out of Bounds")
        else:
            pbi_id = request.POST.get('pbi')
            pbi = get_object_or_404(ProductBacklogItem, pk=pbi_id)
            pbi.name = request.POST.get('newName')
            pbi.desc = request.POST.get('newDesc')
            self.updatePriorities(request, pk)
            pbi.storypoints = request.POST.get('newSto')
            pbi.priority = request.POST.get('newPri')
            pbi.status = request.POST.get('newSta')
            pbi.save()
            return HttpResponseRedirect(reverse('backtrack:project_pb', args=(pbi.project.pk,)))

    def checkPriority(self, request, pk):
        pbi_id = request.POST.get('pbi')
        pbi = get_object_or_404(ProductBacklogItem, pk=pbi_id)
        max_priority = pbi.project.productbacklogitem_set.all().count()
        newPri = int(request.POST.get('newPri'))

        if newPri > max_priority or newPri <= 0:
            return False
        else:
            return True

    def updatePriorities(self, request, pk):
        pbi_id = request.POST.get('pbi')
        pbi = get_object_or_404(ProductBacklogItem, pk=pbi_id)
        old_priority = int(pbi.priority)
        max_priority = pbi.project.productbacklogitem_set.all().count()
        new_priority = int(request.POST.get('newPri'))

        if old_priority == new_priority:
            return

        pbis = pbi.project.productbacklogitem_set.all()
        print(pbis)
        if old_priority < new_priority:
            for i in pbis:
                if i.priority <= new_priority and i.priority > old_priority:
                    if i.priority == old_priority:
                        pass
                    else:
                        temp = i.priority
                        i.priority = temp - 1
                        i.save()
        else:
            for i in pbis:
                if i.priority >= new_priority and i.priority < old_priority:
                    if i.priority == old_priority:
                        pass
                    else:
                        temp = i.priority
                        i.priority = temp + 1
                        i.save()
