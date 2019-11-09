from apscheduler.schedulers.background import BackgroundScheduler
from projectUpdater import backtrackscheduler
from datetime import date


#the flow of using the scheduler for sprints should be like this
#create a sprint instance. when a sprint is created, it will have an interval and start date.
#During the creation of the sprint, call the Backtrackscheduler.add_job to call end of sprint function
#when end of sprint happens, do things w pbi (return to product backlog) & create a new sprint
#the creation of the new sprint triggers the creation of a new job
#check the end datetime of project to make sure that last sprint is scheduled and no more sprints are created

#might have to do shenanigans with timezones :((

scheduler = BackgroundScheduler()

def start():
    scheduler.start()

def add_job(date):
    scheduler.add_job(backtrackscheduler.test_schedule, 'date', run_date=date)

def schedule_end_sprint_job(date):
    scheduler.add_job(backtrackscheduler.end_sprint_events, 'date', run_date=date)
