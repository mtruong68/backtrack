import datetime
from backtrackapp.models import Project, ProductBacklogItem, Sprint, User, ProjectTeam, Task

def end_sprint_events(oldsprint):
    new_sprint = create_new_sprint
    new_sprint.sprintEndEvents


def create_new_sprint(oldsprint):
    new_sprint = Sprint()
    new_sprint.number = oldsprint.number + 1
    new_sprint.interval = oldsprint.interval
    new_sprint.project = oldsprint.project
    new_sprint.start_date = oldsprint.start_date + oldsprint.interval
    new_sprint.save()
    return new_sprint

def remove_PBI_from_sprint_end(oldsprint):
