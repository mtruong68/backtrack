Backtrack application for Scrum Management

Django 2.2.6

To run locally on your machine
`$ python manage.py runserver`

Every time you make changes to the models in the db
```
$ python manage.py makemigrations backtrackapp
$ python manage.py migrate
```
If you create a new file you must restart the server
(Does not hold true for modifying files)
