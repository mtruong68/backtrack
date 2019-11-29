# Backtrack application for Scrum Management
Built with Python v 3.5.2 and Django 2.2.6

## current todo
* add sprint timing functionality, figure out what to do if a project has no sprints yet
* prevent users who are not product owners from adding pbi

* clean up the code!!! clean up task/pbi form
* figure out the many-to-many manager thing

* allow deletion of project
* allow modification of project (can add or delete users on dev team/scrum master)

* ***WRITE TESTS***
* deploy server to heroku or some other host

To run locally on your machine:
`$ python manage.py runserver`

Note: Backtrack is the project name, backtrackapp is the app name (confusing, I know. sorry)

*Links to use Backtrack:*
localhost:8000/
(will lead to the login page)
*On using the Django shell*
```
$ python manage.py shell
> from backtrackapp.models import $MODELS
> p = Project(name="test", desc="a test project")
> p.save()
```
And then you can add/delete/query the db.
And if you want to create new users in the shell:
(Do not create w regular user object as that cannot create correct passwords)
```
> User.objects.create_user(**data)
```
To the test the interface, you can load in some data in the console:
Currently in initial data, the usernames are the team members and the passwords are all password
And to save the state of a database, you can dump data as well
```
$ python manage.py dumpdata backtrackapp>backtrackapp/fixtures/$FILENAME
$ python manage.py loaddata initialdata.json
```

Every time you make changes to the models.py for the backtrackapp (does not apply to inserting/deleting items in the database using forms/shell)
```
$ python manage.py makemigrations backtrackapp
$ python manage.py migrate
```

If you want to drop the entire database:
```
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc"  -delete
rm db.sqlite3
```
or run `./dropdb.sh`


If you create a new file you must restart the server
(Does not hold true for modifying files)
