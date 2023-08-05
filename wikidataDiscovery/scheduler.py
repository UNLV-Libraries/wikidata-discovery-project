"""Scheduler continuously runs on its own thread while executing any pending jobs at each
elapsed time interval (seconds).
"""
import threading
import time
import schedule
from discover import db
from wikidataDiscovery import logs
import datetime


def run_in_background(interval=60):
    cease_continuous_run = threading.Event()

    class SchedulingThread(threading.Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                schedule.run_pending()
                time.sleep(interval)

    continuous_thread = SchedulingThread()
    continuous_thread.start()
    return cease_continuous_run


# Job: cache all app wikidata in backend.
def cache_wikidata():
    dt = datetime.datetime.now()
    m = db.cache_all()
    print(str(dt) + ': ' + m)


# Job: rotate logs, making issue.log issue.log.1, etc.
def rotate_logs():
    logs.rotate_logs()


# list of jobs that will run
schedule.every().day.at('23:58').do(cache_wikidata)
schedule.every().day.at('00:05').do(rotate_logs)

# Start the background thread
stop_run_continuously = run_in_background()

# Stop the background thread
# stop_run_continuously.set()
