import sched
import threading
from discover import db
from wikidataDiscovery import logs
from .wf_utils import update_cache_log
from datetime import datetime, time
import time as just_time


class WfScheduler:
    _initialized = False
    _started = False

    def __init__(self, reload_hour, reload_min):
        if not self._initialized:
            self.reload_hour = reload_hour
            self.reload_min = reload_min
            print('initializing scheduler')
            self.s = sched.scheduler(just_time.time, just_time.sleep)
            self.thread1 = threading.Thread(name='background scheduler', target=self.s.run)
            self.thread2 = threading.Thread(name='reload clock', target=self.check_for_reload)
            self.jobs = {
                'cache_corp_bodies': (self.cache_corp_bodies, 5, 55),  # tuples contain action to run, hour, minute
                'cache_oral_histories': (self.cache_oral_histories, 5, 56),
                'cache_people': (self.cache_people, 5, 57),
                'cache_collections': (self.cache_collections, 5, 58),
                'rotate_logs': (self.rotate_logs, 5, 59),
            }
            self.thread1.start()
            self.thread2.start()
            self._started = True
            self._initialized = True

    def check_for_reload(self):
        # print('checking')
        d = datetime.now()
        hr = d.hour
        mn = d.minute
        if self.reload_hour == hr and self.reload_min == mn:
            self.s.empty()
            self.load_scheduler()
            # print('reloaded')

        just_time.sleep(60)  # 1 second less than Clock period=60
        self.check_for_reload()

    def load_scheduler(self):
        for k, v in self.jobs.items():
            self.add_to_queue(k)

        update_cache_log(str(self.s.queue))
        print(self.s.queue)

    def add_to_queue(self, job_name):
        # create a future time for the incoming job
        job_data = self.jobs[job_name]
        d1 = datetime.date(datetime.today())
        new_date = d1
        new_time = time(hour=job_data[1], minute=job_data[2])
        new_dt = datetime.combine(new_date, new_time)

        # add job to queue
        self.s.enterabs(new_dt.timestamp(), 1, job_data[0])

    @staticmethod
    def cache_collections(self):
        msg = db.cache_collections()
        update_cache_log(msg)

    @staticmethod
    def cache_corp_bodies(self):
        msg = db.cache_corp_bodies()
        update_cache_log(msg)

    @staticmethod
    def cache_oral_histories(self):
        msg = db.cache_oral_histories()
        update_cache_log(msg)

    @staticmethod
    def cache_people(self):
        msg = db.cache_people()
        update_cache_log(msg)

    # Job: rotate logs, making issue.log & issue.log.1 - .6
    @staticmethod
    def rotate_logs(self):
        logs.rotate_logs()

    def print_queue(self):
        print(self.s.queue)

