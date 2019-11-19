from django.views import generic
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy

from .forms import NewProjectForm, NewPBIForm, NewTaskForm, ProjectTeamForm, CustomUserCreationForm
from .models import Project, ProductBacklogItem, Sprint, User, ProjectTeam, Task

#Sees if user has access to a project by looking into a project's project team
#Returns true if user in a project team, else, false.
def has_access(user, project_pk):
    project = get_object_or_404(Project, pk=project_pk)
    pt = ProjectTeam.objects.filter(project=project).first()
    if pt.scrum_master == user or pt.product_owner == user:
        return True
    for dev in pt.dev_team.all():
        if dev == user:
            return True
    return False

#Sees if user has permission to add/modify/delete PBI
#True if user is product owner and it is their current project
def is_productowner(user, project_pk):
    access = False
    project = get_object_or_404(Project, pk=project_pk)
    pt = ProjectTeam.objects.filter(project=project).first()
    if pt.product_owner == user and user.current_project == project:
        return True
    return False

#Sees if user has permission to add/modify/delete Task
#True if user is on the dev team and is their current project
def is_dev(user, project_pk):
    access = False
    project = get_object_or_404(Project, pk=project_pk)
    pt = ProjectTeam.objects.filter(project=project).first()
    for dev in pt.dev_team.all():
        if dev == user and user.current_project == project:
            return True
    return False

#Sees if the user is the scrum master (manager)
#True if user is scrum master and is their current project
def is_scrummaster(user):
    if user.role == 'M':
        return True
    return False

class SignUpView(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'

#We need to create different index views based on the type of role the user has
#if no current project or is the product owner, show the product backlog first
#if a developer, show the task view
#do the manager stuff later
class IndexView(generic.View):

    def productOwnerIndexPage(self, request, user, currentProjectID):
        project = get_object_or_404(Project, pk=currentProjectID)

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

    def developerIndexPage(self, request, user, currentProjectID):
        currentProject = get_object_or_404(Project, pk=currentProjectID)
        sprint = get_object_or_404(Sprint, project=currentProject)
        return render(request, 'backtrackapp/projectsbview.html', {'sprint':sprint, 'project': sprint.project})

    def scrumMasterIndexPage(self, request, user):
        projectTeamsManaged = ProjectTeam.objects.filter(scrum_master=user).all()
        return render(request, 'backtrackapp/projectview.html', {'projectTeamsManaged_list':projectTeamsManaged})

    def get(self, request):
        user = request.user
        if user.is_authenticated:
            project = get_object_or_404(Project, pk=user.current_project.pk)
            if is_productowner(user, project.pk):
                return self.productOwnerIndexPage(request, user, project.pk)
            if is_dev(user, project.pk):
                return self.developerIndexPage(request, user, project.pk)
            if is_scrummaster(user):
                return self.scrumMasterIndexPage(request, user)
        else:
            return HttpResponseRedirect(reverse('login'))

#Views handling the client creating a New Project
class NewProjectView(generic.View):
    def get(self, request):
        user = request.user
        if user.is_authenticated:
            if user.current_project != None:
                #if a user currently has a current project, do not allow them access to forms to create new projects
                return HttpResponseRedirect(reverse('backtrack:index'))
            else:
                projects = Project.objects.all()
                projectForm = NewProjectForm()
                teamForm = ProjectTeamForm()
                teamForm.fields['scrum_master'].queryset = User.objects.filter(current_project=None).exclude(pk=user.pk)
                teamForm.fields['dev_team'].queryset = User.objects.filter(current_project=None).exclude(pk=user.pk)

                return render(request,
                'backtrackapp/newproject.html',
                {'projectForm': projectForm, 'teamForm': teamForm, 'projects': projects})
        else:
            return HttpResponseRedirect(reverse('login'))

    def post(self, request):
        user = request.user
        projectForm = NewProjectForm(request.POST)
        teamForm = ProjectTeamForm(request.POST)

        if self.checkMembers(request, user) == False:
            return HttpResponse("Form is incorrect")

        if teamForm.is_valid() and projectForm.is_valid():
            newProject = projectForm.save()
            newProject.save()
            newTeam = teamForm.save(commit=False)
            newTeam.project = newProject
            newTeam.product_owner = user
            newTeam.save()
            self.update_dev_team(request, newTeam)
            self.update_team_current_project(newTeam)
            return HttpResponseRedirect(reverse('backtrack:project_pb', args=(newProject.id,)))

        return render(request,
        'backtrackapp/newproject.html',
        {'projectForm': projectForm, 'teamForm': teamForm})

    #Will return true if there are no duplicates selected project team and all
    #selected members are currently available (current_project = false)
    def checkMembers(self, request, user):
        dev_team = request.POST.getlist('dev_team')
        dev_team.append(request.POST.get('scrum_master'))
        dev_team.append(str(user.id))
        result = True if len(dev_team) == len(set(dev_team)) else False

        for member_id in dev_team:
            member = get_object_or_404(User, pk=int(member_id))
            if member.current_project != None:
                return False

        return result

    #I do not understand why saving the form does not work in this context
    #but here is a dumb workaround method
    def update_dev_team(self, request, newTeam):
        dev_team = request.POST.getlist('dev_team')
        for member_id in dev_team:
            newTeam.dev_team.add(User.objects.get(pk=int(member_id)))
            newTeam.save()

    def update_team_current_project(self, newTeam):
        project = newTeam.project
        newTeam.product_owner.current_project = project
        newTeam.product_owner.save()
        newTeam.scrum_master.current_project = project
        newTeam.scrum_master.save()
        for dev in newTeam.dev_team.all():
            print(dev.name)
            dev.current_project = project
            dev.save()

#Views handling the client accessing the Product Backlog
#Maybe make separate view for just looking at the product backlog
class ProjectPBView(generic.View):
    def get(self, request, pk):
        user = request.user
        if user.is_authenticated:
            if has_access(user, pk):
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
                raise Http404("You do not have access to this project")
        else:
            return HttpResponseRedirect(reverse('login'))


    def post(self, request, pk):
        if 'addToSprint' in self.request.POST:
            return self.addToSprint(request, pk)
        if 'createNewPBI' in self.request.POST:
            return self.createNewPBI(request, pk)
        if 'deletePBI' in self.request.POST:
            return self.deletePBI(request, pk)
        if 'splitPBI' in self.request.POST:
            return self.splitPBI(request, pk)
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
class SprintBacklogView(generic.View):
    def get(self, request, pk):
        user = request.user
        if user.is_authenticated:
            sprint = get_object_or_404(Sprint, pk=pk)
            if has_access(user, sprint.project.pk):
                return render(request, 'backtrackapp/projectsbview.html', {'sprint':sprint,
                'project': sprint.project})
            else:
                return Http404("You do not have access to this project")
        else:
            return HttpResponseRedirect(reverse('login'))

#Views handling the client accessing the Project Management Page
class ProjectView(generic.View):
    def get(self, request, pk):
        user = request.user
        if user.is_authenticated:


            projectTeamsManaged = get_object_or_404(ProjectTeam, scrum_master=user)
            projectsInCharge = projectTeamsManaged.project.all()
            return render(request, 'backtrackapp/projectview.html', projectsInCharge)




            sprint = get_object_or_404(Sprint, pk=pk)
            if has_access(user, sprint.project.pk):
                return render(request, 'backtrackapp/projectsbview.html', {'sprint':sprint,
                'project': sprint.project})
            else:
                return Http404("You do not have access to this project")
        else:
            return HttpResponseRedirect(reverse('login'))

class NewTaskView(generic.View):
    def get(self, request, pk):
        user = request.user
        if user.is_authenticated:
            pbi = get_object_or_404(ProductBacklogItem, pk=pk)
            if has_access(user, pbi.project.pk):
                context = {'form': NewTaskForm(initial={'pbi': pbi}), 'pbi': pbi}
                return render(request, 'backtrackapp/newtask.html', context)
            else:
                return Http404("You do not have access to this project")
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
            if has_access(user, task.pbi.project.pk):
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
                return Http404("You do not have access to this project")
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
            if has_access(user, pbi.project_id):
                context = {'form': NewPBIForm(initial={'pbi': pbi}),
                'pbi': pbi}
                return render(request, 'backtrackapp/modifyPBI.html', context)
            else:
                return Http404("You do not have access to this project.")
        else:
            return HttpResponseRedirect(reverse('login'))

    def post(self, request, pk):
        if 'savePBI' in self.request.POST:
            return self.savePBI(request, pk)
        else:
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
