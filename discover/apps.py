from django.apps import AppConfig
from .wf_utils import update_scheduler_log, catch_err
import threading


class DiscoverConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'discover'

    def __init__(self, app_name, app_module):
        super().__init__(app_name, app_module)
        self.wfs = None

    def ready(self):  # overrides method of AppConfig
        from .wf_sched import WfScheduler
        self.wfs = WfScheduler()
        try:
            if self.wfs.initialized:
                scheduler_thread = threading.Thread(name='scheduler thread',
                                                    target=self.wfs.run_scheduler(), daemon=True)
                scheduler_thread.start()
                print('scheduler thread started...')
            else:
                update_scheduler_log("scheduler failed to start.")
                print('scheduler failed to start.')
        except Exception as e:
            catch_err(e, 'apps.ready')
