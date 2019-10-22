from django.db import models

class Project(models.Model):
    name = models.CharField(max_length=256)
    desc = models.TextField()
    def __str__(self):
        return self.name

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
    status = models.CharField(max_length=1, choices=STATUS)
    project = models.ForeignKey(Project,
    on_delete = models.CASCADE)

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
    status = models.CharField(max_length=1, choices=STATUS)
    pbi = models.ForeignKey(ProductBacklogItem,
    on_delete = models.CASCADE)
    assignment = models.ManyToManyField(User,
    on_delete = models.PROTECT)

    def __str__(self):
        return self.name

class User(models.Model):
    name = models.CharField(max_length=256)
    available = models.BooleanField(default = True)
