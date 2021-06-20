from django.apps import AppConfig


class ServicesExamplesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'services.examples'

    def ready(self):
        import services.examples.own_service_example
