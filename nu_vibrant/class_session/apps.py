from django.apps import AppConfig


class ClassSessionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'nu_vibrant.class_session'
    
    def ready(self):
        import nu_vibrant.class_session.signals
        import nu_vibrant.class_session.events
