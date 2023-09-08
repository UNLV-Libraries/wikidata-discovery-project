import sched
import threading
from discover import db
from wikidataDiscovery import logs
from .wd_utils import update_cache_log
from datetime import datetime, timedelta, time
import time as just_time


class WfScheduler:
    _initialized = False
    _started = False

    def __init__(self):
        if not self._initialized:
            print('initializing')
            self.s = sched.scheduler(just_time.time, just_time.sleep)
            self.thread = threading.Thread(name='background scheduler', target=self.s.run)

            self.jobs = {
                'cache_corp_bodies': (self.cache_corp_bodies, 23, 54),  # tuples contain action to run, hour, minute
                'cache_oral_histories': (self.cache_oral_histories, 23, 55),
                'cache_people': (self.cache_people, 23, 56),
                'cache_collections': (self.cache_collections, 23, 57),
                'rotate_logs': (self.rotate_logs, 23, 58),
            }
            self._initialized = True

    def load_scheduler(self):
        if not self._started:
            for k, v in self.jobs.items():
                self.add_to_queue(k)

            print(self.s.queue)

    def start_scheduler(self):
        self.thread.start()
        self._started = True

    def stop_scheduler(self):
        self.s.empty()
        self.thread.join(timeout=1)

    def add_to_queue(self, job_name):
        # create a future time for the incoming job
        job_data = self.jobs[job_name]
        d1 = datetime.date(datetime.today())
        if self._started:
            new_date = d1 + timedelta(days=1)
        else:
            new_date = d1
        new_time = time(hour=job_data[1], minute=job_data[2])
        new_dt = datetime.combine(new_date, new_time)

        # add job to queue
        self.s.enterabs(new_dt.timestamp(), 1, job_data[0])

    def cache_collections(self):
        msg = db.cache_collections()
        update_cache_log(msg)
        self.add_to_queue('cache_collections')

    def cache_corp_bodies(self):
        msg = db.cache_corp_bodies()
        update_cache_log(msg)
        self.add_to_queue('cache_corp_bodies')

    def cache_oral_histories(self):
        msg = db.cache_oral_histories()
        update_cache_log(msg)
        self.add_to_queue('cache_oral_histories')

    def cache_people(self):
        msg = db.cache_people()
        update_cache_log(msg)
        self.add_to_queue('cache_people')

    # Job: rotate logs, making issue.log & issue.log.1 - .6
    def rotate_logs(self):
        logs.rotate_logs()
        self.add_to_queue('rotate_logs')

    def print_queue(self):
        print(self.s.queue)