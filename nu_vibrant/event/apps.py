from django.apps import AppConfig


class EventConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'nu_vibrant.event'
    
    def ready(self):
        pass
