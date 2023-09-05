import threading
import time
import schedule
from discover import db
from wikidataDiscovery import logs
from .wd_utils import update_cache_log


def check_queue():
    schedule.run_pending()


class Monitor:
    def __init__(self):
        self.stop = False

    def start_monitor(self):
        print("Run start_monitor")
        while not self.stop:
            check_queue()
            # print("inside while loop")
            time.sleep(300)

    def stop_monitoring(self):
        print("Run stop_monitoring")
        self.stop = True


def run_monitor():
    m = Monitor()
    t = threading.Thread(name='background monitor', target=m.start_monitor)
    t.start()


def cache_collections():
    msg = db.cache_collections()
    update_cache_log(msg)


def cache_corp_bodies():
    msg = db.cache_corp_bodies()
    update_cache_log(msg)


def cache_oral_histories():
    msg = db.cache_oral_histories()
    update_cache_log(msg)


def cache_people():
    msg = db.cache_people()
    update_cache_log(msg)


# Job: rotate logs, making issue.log & issue.log.1 - .6
def rotate_logs():
    logs.rotate_logs()


def test_job():
    print('background thread works')


# Use schedule module to define jobs for specific times
# schedule.every().day.at('15:20').do(cache_collections)
# schedule.every().day.at('14:20').do(cache_corp_bodies)
# schedule.every().day.at('14:18').do(cache_oral_histories)
# schedule.every().day.at('14:16').do(cache_people)
schedule.every().day.at('00:01').do(rotate_logs)
# schedule.every(5).seconds.do(test_job)


