# Backtrack application for Scrum Management
Built with Python v 3.5.2 and Django 2.2.6

## current todo
* add sprint timing functionality, figure out what to do if a project has no sprints yet
* right now, link project teams and projects together
* ***WRITE TESTS***
* deploy server to heroku or some other host
* please someone... do some css magic on it... its so ugly rn

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
```
And then you can add/delete/query the db.
And if you want to create new users in the shell:
(Do not create w regular user object as that cannot create correct passwords)
```
> User.objects.create_user(**data)
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
