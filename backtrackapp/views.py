from django.views import generic
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy

from html import unescape

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


class IndexView(generic.View):
    def get(self, request):
        user = request.user
        if user.is_authenticated:
            if is_scrummaster(user):
                return ProjectView.get(self, request, None)
            else:
                if user.current_project != None:
                    project = get_object_or_404(Project, pk=user.current_project.pk)
                    return ProjectView.get(self, request, project.pk)
                else:
                    return render(request, 'backtrackapp/idleDeveloper.html')
        else:
            return HttpResponseRedirect(reverse('login'))





#Views handling the client accessing the Project Management Page
class ProjectView(generic.View):
    def get(self, request, currentProjectID):
        user = request.user
        if user.is_authenticated:
            if is_scrummaster(user):
                projectTeamsManaged = ProjectTeam.objects.filter(scrum_master=user).all()
                return render(request, 'backtrackapp/scrumMasterProject.html', {'projectTeamsManaged_list':projectTeamsManaged})
            else:
                project = get_object_or_404(Project, pk=currentProjectID)
                if is_productowner(user, currentProjectID):
                    return render(request, 'backtrackapp/productOwnerProject.html', {'currentProject':project})
                else:
                    return render(request, 'backtrackapp/busyDeveloperProject.html', {'currentProject':project})
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

                return render(request, 'backtrackapp/_new_project.html', {'projectForm': projectForm, 'teamForm': teamForm})
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

        return render(request, 'backtrackapp/_new_project.html', {'projectForm': projectForm, 'teamForm': teamForm})

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
class ProductBacklogView(generic.View):
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
                    latestSprint = sprints.latest('creation_time')
                else:
                    latestSprint = None

                context = {'form': NewPBIForm(initial={'project': project}), 'project': project, 'latestSprint': latestSprint, 'pbi_cum_points_list': pbi_cum_points_list}

                if is_scrummaster(user):
                    return render(request, 'backtrackapp/scrumMasterProductBacklog.html', context)
                elif is_productowner(user, project.pk):
                    return render(request, 'backtrackapp/productOwnerProductBacklog.html', context)
                else:
                    return render(request, 'backtrackapp/busyDeveloperProductBacklog.html', context)
            else:
                raise Http404("You do not have access to this project")
        else:
            return HttpResponseRedirect(reverse('login'))

    def post(self, request, pk):
        if request.POST.get('pbi_id') != None:
            pbi_id = int(request.POST.get('pbi_id'))

        if 'addToSprint' in request.POST:
            return self.addToSprint(request, pbi_id, pk)
        if 'createNewPBI' in request.POST:
            return self.createNewPBI(request, pbi_id)
        if 'deletePBI' in request.POST:
            return self.deletePBI(request, pbi_id)
        if 'splitPBI' in request.POST:
            return self.splitPBI(request, pbi_id)
        if 'modifyPBI' in request.POST:
            return HttpResponseRedirect(reverse('backtrack:modify_PBI', args=(pbi_id,)))
        else:
            #this is a stub method and needs to be changed
            print(form.errors)
            return HttpResponse("Did not work.")

    def addToSprint(self, request, pbi_id, project_id):
        project = get_object_or_404(Project, pk=project_id)
        latestSprint = project.getLatestSprint()
        pbi = get_object_or_404(ProductBacklogItem, pk=pbi_id)
        pbi.sprint = latestSprint
        pbi.save()
        return HttpResponseRedirect(reverse('backtrack:project_pb', args=(project_id,)))

    def deletePBI(self, request, pk):
        pbi = get_object_or_404(ProductBacklogItem, pk=pk)
        self.updatePrioritiesDelete(pk, pbi.priority)
        pbi.delete()
        return HttpResponseRedirect(reverse('backtrack:project_pb', args=(pk,)))

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





class NewPBIView(generic.View):
    def get(self, request, pk):
        user = request.user
        if user.is_authenticated:
            if has_access(user, pk):
                project = get_object_or_404(Project, pk=pk)
                context = {'form': NewPBIForm(initial={'project': project})}
                return render(request, 'backtrackapp/_new_PBI.html', context)
            else:
                return Http404("You do not have access to this project.")
        else:
            return HttpResponseRedirect(reverse('login'))

    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        form = NewPBIForm(request.POST, initial={'project': project})
        if form.is_valid():
            newPBI = form.save(commit=False)
            newPBI.project = project
            if ProductBacklogView.checkPriority(self, pk, request.POST.get('priority')) == False:
                return HttpResponse("Priority Out of Bounds")
            else:
                ProductBacklogView.updatePriorities(self, request, pk, request.POST.get('priority'))
                newPBI.save()
                #redirect back to product backlog view
                return HttpResponseRedirect(reverse('backtrack:project_pb', args=(pk,)))
        else:
            #this is a stub method and needs to be changed
            print(form.errors)
            return HttpResponse("Did not work.")





class ModifyPBIView(generic.View):
    #need to sort pbi by priority and show in order of priority
    def get(self, request, pk):
        user = request.user
        if user.is_authenticated:
            pbi = get_object_or_404(ProductBacklogItem, pk=pk)
            if has_access(user, pbi.project_id):

                choices = [
                    {'value': 'NS', 'status':'Not Started'},
                    {'value': 'IP', 'status':'In Progress'},
                    {'value': 'C', 'status': 'Complete'}
                ]

                for choice in choices:
                    if choice['value'] == pbi.status:
                        choice['selected'] = "selected"

                context = {'form': NewPBIForm(initial={'pbi': pbi}), 'pbi': pbi, 'choices': choices}
                return render(request, 'backtrackapp/_modify_PBI.html', context)
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





#Views handling the client accessing the Sprint Backlog
class SprintBacklogView(generic.View):
    def get(self, request, pk):
        user = request.user
        if user.is_authenticated:
            if has_access(user, pk):
                project = get_object_or_404(Project, pk=pk)
                sprint = Sprint.objects.filter(project=project).all()
                latestSprint = project.getLatestSprint()

                return self.renderSprint(request, latestSprint, project)

            else:
                return Http404("You do not have access to this project")
        else:
            return HttpResponseRedirect(reverse('login'))

    def post(self, request, pk):
        #allow user to choose which sprint they want to view and then render the correct sprint w tasks & pbi
        user = request.user
        project = get_object_or_404(Project, pk=pk)
        latestSprint = project.getLatestSprint()

        #possible methods of posting
        #getting a sprint sprint number

        if request.POST.get('sprint_id') != None:
            sprint_id = request.POST.get('sprint_id')
            sprint = get_object_or_404(Sprint, pk=sprint_id)
            return self.renderSprint(request, sprint, project)
        if request.POST.get('sprint_action') != None:
            if latestSprint == None or latestSprint.status == 'C':
                return self.createNewSprint(project)
            else:
                if latestSprint.status == 'NS':
                    project.startCurrentSprint()
                    return HttpResponseRedirect(reverse('backtrack:project_sb', args=(latestSprint.pk, )))
                elif latestSprint.status =='IP':
                    project.endCurrentSprint()
                    return HttpResponseRedirect(reverse('backtrack:project_sb', args=(latestSprint.pk, )))

        #what developers can do for tasks in pbi
        if request.POST.get('add_task') != None:
            pbi_id = request.POST.get('pbi_id')
            return HttpResponseRedirect(reverse('backtrack:new_task', args=(pbi_id,)))
        if request.POST.get('delete_task') != None:
            return self.deleteTask(request, latestSprint)
        if request.POST.get('modify_task') != None:
            return self.modifyTask(request, pk)

    def deleteTask(self, request, latestSprint):
        task_id = request.POST.get('task_id')
        Task.objects.get(pk=task_id).delete()
        return HttpResponseRedirect(reverse('backtrack:project_sb', args=(latestSprint.pk, )))

    def modifyTask(self, request, pk):
        task_id = request.POST.get('task_id')
        return HttpResponseRedirect(reverse('backtrack:modify_task', args=(task_id,)))

    def createNewSprint(self, project):
        newSprint = project.createNewSprint()
        newSprint.save()
        return HttpResponseRedirect(reverse('backtrack:project_sb', args=(newSprint.pk,)))

    def renderSprint(self, request, sprint, project):
        user = request.user

        tasksInAllSprintPBIs = []

        sprintPBI_set = ProductBacklogItem.objects.filter(sprint=sprint).all()

        for sprintPBI in sprintPBI_set:
            task_set = Task.objects.filter(pbi=sprintPBI).all()
            for task in task_set:
                tasksInAllSprintPBIs.append(task)

        latestSprint = project.getLatestSprint()
        if latestSprint == None or latestSprint.status == 'C':
            status = 1
        elif latestSprint.status == 'NS':
            status = 2
        else:
            status = 3

        context = {'sprint':sprint, 'project': project, 'sprintPBI_set': sprintPBI_set, 'status':status}

        if is_scrummaster(user):
            return render(request, 'backtrackapp/scrumMasterSprintBacklog.html', context)
        elif is_productowner(user, project.pk):
            return render(request, 'backtrackapp/productOwnerSprintBacklog.html', context)
        else:
            return render(request, 'backtrackapp/busyDeveloperSprintBacklog.html', context)




class NewTaskView(generic.View):
    def get(self, request, pk):
        user = request.user
        if user.is_authenticated:
            pbi = get_object_or_404(ProductBacklogItem, pk=pk)
            if has_access(user, pbi.project.pk):
                availableUsers = ProjectTeam.objects.filter(project=pbi.project).first().dev_team.all()
                context = {'form': NewTaskForm(initial={'pbi': pbi}),
                'pbi': pbi, 'availableUsers': availableUsers}
                return render(request, 'backtrackapp/_new_task.html', context)
            else:
                return Http404("You do not have access to this project")
        else:
            return HttpResponseRedirect(reverse('login'))

    def post(self, request, pk):
        if 'addTask' in request.POST:
            return self.addTask(request, pk)
        else:
            #this is a stub method and needs to be changed
            print(form.errors)
            return HttpResponse("Did not work.")

    def addTask(self, request, pk):
        pbi = get_object_or_404(ProductBacklogItem, pk=pk)
        form = NewTaskForm(request.POST, initial={"pbi":pbi})
        if form.is_valid():
            newTask = form.save(commit=False)
            newTask.pbi = pbi
            newTask.status = 'NS'
            newTask.assignment = get_object_or_404(User, pk=request.POST.get('assignment'))
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
            project_id = task.pbi.project.pk
            project = get_object_or_404(Project, pk=project_id)

            if has_access(user, project_id):
                choices = [
                    {'value': 'NS', 'status':'Not Started'},
                    {'value': 'IP', 'status':'In Progress'},
                    {'value': 'C', 'status': 'Complete'}
                ]
                for choice in choices:
                    if choice['value'] == task.status:
                        choice['selected'] = "selected"

                availableUsers = ProjectTeam.objects.filter(project=project).first().dev_team.all()

                context = {'task':task, 'choices': choices, 'availableUsers': availableUsers}
                return render(request, 'backtrackapp/_modify_task.html', context)
            else:
                return Http404("You do not have access to this project")
        else:
            return HttpResponseRedirect(reverse('login'))

    def post(self, request, pk):
        if 'deleteUser' in self.request.POST:
            return self.deleteUserFromTask(request, pk)
        if 'modifyTask' in self.request.POST:
            return self.modifyTask(request, pk)

    #check to make sure that some user is assigned
    def modifyTask(self, request, pk):
        print(request.POST)
        task = get_object_or_404(Task, pk=pk)
        task.name = request.POST.get('name')
        task.desc = request.POST.get('desc')
        task.burndown = request.POST.get('burndown')
        task.status = request.POST.get('status')
        task.assignment = get_object_or_404(User, pk=request.POST.get('assignment'))
        task.save()
        return HttpResponseRedirect(reverse('backtrack:modify_task', args=(pk,)))
