from django.apps import AppConfig
import signal
from .wf_utils import update_scheduler_log


class DiscoverConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'discover'

    def __init__(self, app_name, app_module):
        super().__init__(app_name, app_module)
        self.wfs = None

    # def ready(self):  # overrides method of AppConfig
        # from .wf_sched import WfScheduler
         #self.wfs = WfScheduler(7, 30)
        # if self.wfs.started:
            # print('scheduler started')
        #    update_scheduler_log("scheduler started")
        #else:
        #    update_scheduler_log("scheduler failed to start.")
        # signal.signal(signal.SIGTERM, self.stop_wf_scheduler)

    # def stop_wf_scheduler(self):
    #     self.wfs.stop_scheduler()
