# Backtrack application for Scrum Management
Built with Python v 3.5.2 and Django 2.2.6

## current todo
* allow deletion/modification of projects on the interface
* allow modification/refinement of pbis on the interface
* create/modify/add tasks
* WRITE TESTS
* deploy server to heroku
* please someone... do some css magic on it... its so ugly rn

To run locally on your machine:
`$ python manage.py runserver`

Note: Backtrack is the project name, backtrackapp is the app name (confusing, I know. sorry)

*Links to use Backtrack:*
localhost:8000/backtrack/
localhost:8000/backtrack/<project_id>/productbacklog
*On using the Django shell*
```
$ python manage.py shell
> import backtrackapp.models import $MODELS
```
And then you can add/delete/query the db. Currenly, in the db, there is a sprint and two users (Bob & Kelly)... please do not erase them (yet). I want them for testing purposes!

*do not delete the polls app (yet)!!!*
(I need it for reference)

Every time you make changes to the models.py for the backtrackapp (does not apply to inserting/deleting items in the database using forms/shell)
```
$ python manage.py makemigrations backtrackapp
$ python manage.py migrate
```

If you create a new file you must restart the server
(Does not hold true for modifying files)
