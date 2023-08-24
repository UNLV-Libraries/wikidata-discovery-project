from django.apps import AppConfig


class DiscoverConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'discover'

    def ready(self):  # overrides AppConfig.ready method
        from . import scheduler
        run = scheduler.run_continuously()
        if run:
            print("Scheduler is running.")
