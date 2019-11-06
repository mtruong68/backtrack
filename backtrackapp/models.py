from django.db import models
from django.contrib.auth.models import AbstractUser
import datetime

class User(AbstractUser):
    name = models.CharField(max_length=256)
    def __str__(self):
        return self.name
    #available = models.BooleanField()

class Project(models.Model):
    name = models.CharField(max_length=256)
    desc = models.TextField()
    def __str__(self):
        return self.name

class Sprint(models.Model):
    number = models.PositiveIntegerField()
    start_date = models.DateTimeField(auto_now_add=True)
    project = models.ForeignKey(Project,
    on_delete = models.CASCADE)
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
    assignment = models.ManyToManyField(User)

    def __str__(self):
        return self.name
