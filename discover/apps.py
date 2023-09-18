from django.apps import AppConfig


class DiscoverConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'discover'

    def ready(self):  # method of AppConfig
        from .wf_sched import WfScheduler
        wfs = WfScheduler(5, 46)
        if wfs.started:
            print('scheduler started')



