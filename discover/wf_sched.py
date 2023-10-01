"""Keeps track of time and executes defined jobs on a daily schedule. Clock runs on a separate thread and checks
schedule queue every minute for jobs to run. All jobs are defined as functions in the wf_sched module."""
import sched
import threading
from discover import db
from wikidataDiscovery import logs
from .wf_utils import update_scheduler_log, catch_err
from datetime import datetime, time
import time as just_time


class WfScheduler:
    initialized = False
    started = False
    thread2 = None

    def __init__(self, reload_hour, reload_min):
        if not self.initialized:
            try:
                self.reload_hour = reload_hour
                self.reload_min = reload_min
                print('initializing scheduler')
                self.s = sched.scheduler(just_time.time, just_time.sleep)
                self.thread2 = threading.Thread(name='scheduler clock', target=self.run_clock)
                # All jobs data is stored in self.jobs.
                self.jobs = {
                    'cache_corp_bodies': (cache_corp_bodies, 7, 31),  # tuples contain action to run, hour, & minute
                    'cache_oral_histories': (cache_oral_histories, 7, 32),
                    'cache_people': (cache_people, 7, 33),
                    'cache_collections': (cache_collections, 7, 34),
                    'rotate_logs': (rotate_logs, 7, 35),
                }

                self.thread2.start()
                self.started = True
                self.initialized = True
            except Exception as e:
                catch_err(e, 'WfScheduler.__init__')

    def load_scheduler(self):
        for k, v in self.jobs.items():
            self.add_to_queue(k)

        # print(self.s.queue)

    def add_to_queue(self, job_name):
        # create a future time for the incoming job
        job_data = self.jobs[job_name]
        d1 = datetime.date(datetime.today())
        new_date = d1
        new_time = time(hour=job_data[1], minute=job_data[2])
        new_dt = datetime.combine(new_date, new_time)

        # add job to queue
        self.s.enterabs(new_dt.timestamp(), 1, job_data[0])

    def print_queue(self):
        print(self.s.queue)

    def stop_scheduler(self):
        self.thread2.join(1)


# All functions below are run by the scheduler.
def cache_collections():
    # msg = db.cache_collections()
    # update_scheduler_log(msg)
    print('collections {}'.format(datetime.now()))


def cache_corp_bodies():
    # msg = db.cache_corp_bodies()
    # update_scheduler_log(msg)
    print('corp bodies {}'.format(datetime.now()))


def cache_oral_histories():
    # msg = db.cache_oral_histories()
    # update_scheduler_log(msg)
    print('orals {}'.format(datetime.now()))


def cache_people():
    # msg = db.cache_people()
    # update_scheduler_log(msg)
    print('people {}'.format(datetime.now()))


def rotate_logs():
    # logs.rotate_logs()
    # update_scheduler_log("Issue logs rotated.")
    print('rotate logs {}'.format(datetime.now()))


def scheduler_test():
    print(f'scheduler test {datetime.now()}')


