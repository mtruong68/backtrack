from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.shortcuts import get_object_or_404
import datetime

class Project(models.Model):
    STATUS = (
        ('NS', 'Not Started'),
        ('IP', 'In Progress'),
        ('C', 'Complete'),
    )
    name = models.CharField(max_length=256)
    desc = models.TextField()
    status = models.CharField(max_length=2, choices=STATUS, default='NS')
    startDate = models.DateTimeField(default=timezone.now)
    endDate = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

    def getLatestSprint(self):
        sprints = self.sprint_set.all()
        if len(sprints) == 0:
            return None
        else:
            return sprints.order_by('-creation_time')[0]

    def createNewSprint(self):
        #if you have a current sprint that is in progress, do not allow creation of new sprint
        latestSprint = self.getLatestSprint()

        if latestSprint != None:
            latestNumber = latestSprint.number + 1
            if latestSprint.status != 'C':
                return -1
        else:
            latestNumber = 1;

        sprint = Sprint(number=latestNumber, project=self)
        return sprint

    def startCurrentSprint(self):
        latestSprint = self.getLatestSprint()
        if latestSprint == None or latestSprint.status != 'NS':
            return -1
        else:
            latestSprint.status = 'IP'
        latestSprint.save()

    def endCurrentSprint(self):
        latestSprint = self.getLatestSprint()
        sprintPBIs = latestSprint.productbacklogitem_set.all()

        for PBI in sprintPBIs:
            if PBI.completedTasks():
                PBI.status = "C"
            if PBI.status != "C":
                PBI.sprint = None
                PBI.status = "NS"
                PBI.save()

        latestSprint.status = "C"
        latestSprint.save()


class User(AbstractUser):
    name = models.CharField(max_length=256)
    isManager = models.BooleanField(default = False)
    current_project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name



class ProjectTeam(models.Model):
    teamName = models.CharField(max_length=256, default='New Project Team')
    scrum_master = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='scrum_master')
    product_owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='product_owner')
    dev_team = models.ManyToManyField(User, related_name='devs')
    project = models.ForeignKey(Project, on_delete = models.CASCADE)

    def __str__(self):
        return self.teamName





class Sprint(models.Model):
    STATUS = (
        ('NS', 'Not Started'),
        ('IP', 'In Progress'),
        ('C', 'Complete'),
    )
    number = models.PositiveIntegerField()
    creation_time = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=2, choices=STATUS, default='NS')
    totalCapacity = models.PositiveIntegerField(default=0)
    project = models.ForeignKey(Project, on_delete = models.CASCADE)

    def __str__(self):
        return str(self.number)

    def totalEstimatedEffort(self):
        effort = 0
        pbis = self.productbacklogitem_set.all()

        for pbi in pbis:
            tasks = pbi.task_set.all()
            for task in tasks:
                effort += task.estimate

        return effort

    def totalBurndown(self):
        burndown = 0
        pbis = self.productbacklogitem_set.all()

        for pbi in pbis:
            tasks = pbi.task_set.all()
            for task in tasks:
                burndown += task.burndown

        return burndown

    def totalEffortRemaining(self):
        return self.totalEstimatedEffort() - self.totalBurndown()




class ProductBacklogItem(models.Model):
    STATUS = (
        ('NS', 'Not Started'),
        ('IP', 'In Progress'),
        ('C', 'Complete'),
    )
    name = models.CharField(max_length=256)
    desc = models.TextField()
    priority = models.PositiveIntegerField()
    storypoints = models.PositiveIntegerField()
    status = models.CharField(max_length=2, choices=STATUS, default='NS')
    project = models.ForeignKey(Project, on_delete = models.CASCADE)
    sprint = models.ForeignKey(Sprint, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

    def totalBurndown(self):
        burndown = 0
        tasks = self.task_set.all()
        for task in tasks:
            burndown += task.burndown
        return burndown

    def totalEstimatedEffort(self):
        effort = 0
        tasks = self.task_set.all()
        for task in tasks:
            effort += task.estimate
        return effort

    def totalEffortRemaining(self):
        return self.totalEstimatedEffort() - self.totalBurndown()

    def completedTasks(self):
        tasks = self.task_set.all()

        if len(tasks) == 0:
            return False

        for task in tasks:
            if task.status != 'C':
                return False
        return True


class Task(models.Model):
    STATUS = (
        ('NS', 'Not Started'),
        ('IP', 'In Progress'),
        ('C', 'Complete'),
    )
    name = models.CharField(max_length=256)
    desc = models.TextField()
    status = models.CharField(max_length=2, choices=STATUS, default='NS')
    burndown = models.PositiveIntegerField(default=0)
    estimate = models.PositiveIntegerField()
    pbi = models.ForeignKey(ProductBacklogItem, on_delete = models.CASCADE)
    assignment = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

    def remainingEffort(self):
        return self.estimate-self.burndown

    def completeTask(self):
        self.status = 'C'
        self.save()
