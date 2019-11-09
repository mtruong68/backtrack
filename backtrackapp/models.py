from django.db import models
from django.contrib.auth.models import AbstractUser
import datetime

from projectUpdater import backtrackscheduler, updater

class Project(models.Model):
    name = models.CharField(max_length=256)
    desc = models.TextField()
    end_date = models.DateTimeField()
    def __str__(self):
        return self.name

class User(AbstractUser):
    name = models.CharField(max_length=256)
    current_project = models.ForeignKey(Project,
    on_delete=models.SET_NULL, null=True)
    def __str__(self):
        return self.name

class ProjectTeam(models.Model):
    scrum_master = models.ForeignKey(User, on_delete=models.SET_NULL,
    null=True, related_name='scrum_master')
    product_owner = models.ForeignKey(User, on_delete=models.SET_NULL,
    null=True, related_name='product_owner')
    dev_team = models.ManyToManyField(User, related_name='devs')
    project = models.ForeignKey(Project,
    on_delete = models.CASCADE)

class Sprint(models.Model):
    number = models.PositiveIntegerField()
    start_date = models.DateTimeField()
    interval = models.DurationField()
    project = models.ForeignKey(Project,
    on_delete = models.CASCADE)

    #did not yet test this method dont use until testing
    def getLatest(self, proj):
        return Sprint.filter(project=proj).latest('start_date')

    #Use this every time you want
    def sprintEndEvents(self, date, duration):
        if (date + duration < self.project.end_date):
            updater.schedule_end_sprint_job(date + duration)
        else:
            print("cannot schedule")

    def __str__(self):
        return str(self.number)

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
    status = models.CharField(max_length=2, choices=STATUS)
    project = models.ForeignKey(Project,
    on_delete = models.CASCADE)
    sprint = models.ForeignKey(Sprint, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

class Task(models.Model):
    STATUS = (
        ('NS', 'Not Started'),
        ('IP', 'In Progress'),
        ('C', 'Complete'),
    )

    name = models.CharField(max_length=256)
    desc = models.TextField()
    burndown = models.PositiveIntegerField()
    estimate = models.PositiveIntegerField()
    status = models.CharField(max_length=2, choices=STATUS)
    pbi = models.ForeignKey(ProductBacklogItem,
    on_delete = models.CASCADE)
    #assignment = models.ForeignKey(User, on_delete=models.SET_NULL, null = true)
    assignment = models.ManyToManyField(User)

    def __str__(self):
        return self.name
