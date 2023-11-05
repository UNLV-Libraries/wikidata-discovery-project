"""WfScheduler keeps track of time and executes defined jobs on a daily schedule. Called in apps.ready on a
daemon thread. Clock also runs on a separate daemon thread and checks schedule queue every minute for jobs to run.
All jobs are defined as functions in this module."""
import sched
import threading
from discover import db
from wikidataDiscovery import logs
from .wf_utils import update_scheduler_log, catch_err
from datetime import datetime, time
import time as just_time
from .mappings import SCHEDULER_ALARM_TIME

# Process:
# 1. Scheduler instantiates clock class
# 2. scheduler registers its own reload event with clock - self.load_scheduler
# 3. scheduler runs clock
# 4. clock ticks every minute
# 5. at appointed minute, it runs the scheduler's method, load_scheduler; creates new clock at end.


class Event(object):
    def __init__(self):
        self.__event_handlers = []

    def __iadd__(self, handler):
        self.__event_handlers.append(handler)
        return self

    def __isub__(self, handler):
        self.__event_handlers.remove(handler)
        return self

    def __call__(self, *args, **kwargs):
        for eventhandler in self.__event_handlers:
            eventhandler(*args, **kwargs)


class Clock(object):
    def __init__(self, alarm_hour, alarm_min):
        self.hour = alarm_hour
        self.min = alarm_min
        self.next_time = 0
        self.alarm_time = False
        self.onAlarm = Event()
        self.clock_thread = threading.Thread(name='scheduler clock', target=self.run_clock, daemon=True)
        self.clock_thread.start()

    def run_clock(self):
        # check to see if queue needs to be reloaded
        # todo: prevent new clock from loading new scheduler while scheduler is running
        d = datetime.now()
        hr = d.hour
        mn = d.minute
        # print('tick...')
        if self.hour == hr and self.min == mn:
            self.alarm()
        just_time.sleep(60)  # Clock period=60 secs
        self.alarm_time = False
        self.run_clock()  # continue running clock

    def alarm(self):
        self.onAlarm()
        self.alarm_time = True
        return self.alarm_time

    def subscribe_to_alarm(self, obj_method):
        self.onAlarm += obj_method


class WfScheduler:
    initialized = False
    s = None

    def __init__(self):
        if not self.initialized:
            try:
                # All jobs data is stored in self.jobs.
                self.the_clock = Clock(SCHEDULER_ALARM_TIME[0], SCHEDULER_ALARM_TIME[1])
                self.the_clock.subscribe_to_alarm(self.load_scheduler)
                self.jobs = {
                    'cache_corp_bodies': (cache_corp_bodies, 23, 52),  # tuples contain action to run, hour, & minute
                    'cache_oral_histories': (cache_oral_histories, 23, 53),
                    'cache_people': (cache_people, 23, 54),
                    'cache_collections': (cache_collections, 23, 55),
                    'rotate_logs': (rotate_logs, 23, 56),
                }
                self.initialized = True
            except Exception as e:
                catch_err(e, 'WfScheduler.__init__')

    def run_scheduler(self):
        self.s = sched.scheduler(just_time.time, just_time.sleep)

    def load_scheduler(self):
        if self.s.queue.__len__() == 0:  # avoid reload if queue isn't empty
            for k, v in self.jobs.items():
                # create a future time for the incoming job
                job_data = self.jobs[k]
                d1 = datetime.date(datetime.today())
                new_date = d1
                new_time = time(hour=job_data[1], minute=job_data[2])
                new_dt = datetime.combine(new_date, new_time)
                # add job to queue
                self.s.enterabs(new_dt.timestamp(), 1, job_data[0])
            self.s.run()  # start queue processing

            # create new clock object w/ the standard alarm time.
            h = self.the_clock.hour
            m = self.the_clock.min
            self.the_clock = None  # destroy old clock plus the thread it runs on
            self.the_clock = Clock(h, m)  # create new clock
            self.the_clock.subscribe_to_alarm(self.load_scheduler)  # re-subscribe to event

    def print_queue(self):
        print(self.s.queue)


# All functions below are run by the scheduler.
def cache_collections():
    msg = db.cache_collections()
    update_scheduler_log(msg)
    # print('collections {}'.format(datetime.now()))


def cache_corp_bodies():
    msg = db.cache_corp_bodies()
    update_scheduler_log(msg)
    # print('corp bodies {}'.format(datetime.now()))


def cache_oral_histories():
    msg = db.cache_oral_histories()
    update_scheduler_log(msg)
    # print('orals {}'.format(datetime.now()))


def cache_people():
    msg = db.cache_people()
    update_scheduler_log(msg)
    # print('people {}'.format(datetime.now()))


def rotate_logs():
    logs.rotate_logs()
    update_scheduler_log("Issue logs rotated.")
    # print('rotate logs {}'.format(datetime.now()))
