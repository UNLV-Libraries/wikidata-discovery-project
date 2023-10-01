
import threading
from datetime import datetime, time
import time as just_time


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
        self.__hour = alarm_hour
        self.__min = alarm_min
        self.__next_time = 0
        self.alarm_time = False
        self.onAlarm = Event()
        self.clock_thread = threading.Thread(name='scheduler clock', target=self.run_clock, daemon=True)

    def run_clock(self):
        # check to see if queue needs to be reloaded

        d = datetime.now()
        hr = d.hour
        mn = d.minute
        if self.__hour == hr and self.__min == mn:

            print('raise the reload event')

        just_time.sleep(60)  # Clock period=60 secs
        self.run_clock()  # continue running clock

    def alarm(self):
        self.onAlarm()
        self.alarm_time = True
        return self.alarm_time

    def subscribe_to_alarm(self, obj_method):
        self.onAlarm += obj_method

# Attempt 1 (Andre's modified pattern.)
# Scheduler instantiates clock class
# scheduler registers its own reload event with clock - self.reloadthequeue
# scheduler runs clock
# clock ticks every minute
# at appointed minute, it runs the scheduler's method.

# Attempt 2 (follows example pattern)
# .ready method of apps creates a clock object and a scheduler object
# .ready registers scheduler method with clock object
# .ready runs clock
# clock ticks every minute
# at appointed minute, it runs the scheduler method
