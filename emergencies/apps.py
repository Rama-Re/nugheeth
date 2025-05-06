from django.apps import AppConfig


class EmergenciesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'emergencies'

    def ready(self):
        from global_services.googleMap import updater
        updater.start()
