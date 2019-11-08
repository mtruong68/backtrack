from django.apps import AppConfig
from projectUpdater import updater

class BacktrackappConfig(AppConfig):
    name = 'backtrackapp'

    def ready(self):
        updater.start()
