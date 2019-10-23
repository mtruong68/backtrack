#Backtrack application for Scrum Management#
Built with Python v 3.5.2 and Django 2.2.6

##current todo##
* allow deletion of projects on the interface
* link each project view to its own page where you add pbi (via another form view)
* WRITE TESTS
* deploy server to heroku
* make it look a little nicer... not too much

To run locally on your machine:
`$ python manage.py runserver`

Note: Backtrack is the project name, backtrackapp is the app name (confusing, I know. sorry) Links just use backtrack
local links:
localhost:8000/backtrack/
localhost:8000/backtrack/<projectname>

*do not delete the polls app (yet)!!!*
(I need it for reference)


Every time you make changes to the models.py for the backtrackapp (does not apply to inserting/deleting items in the database using forms/shell)
```
$ python manage.py makemigrations backtrackapp
$ python manage.py migrate
```

If you create a new file you must restart the server
(Does not hold true for modifying files)
