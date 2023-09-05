import datetime
import logging
from wikidataDiscovery.settings import BASE_DIR

# the_log = logging.getLogger(__name__)


def catch_err(e, proc=None):
    """General function for error processing."""
    # generic handler for error messages and logging
    from django.utils.safestring import mark_safe
    dt = datetime.datetime.now()
    # global the_log
    the_log = logging.getLogger(__name__)
    try:
        # e contains Exception
        if e.args[0] == 1064:  # bad search string that SQL doesn't like.
            the_message = "You've used an invalid search string. Try again."
        else:
            the_message = str(e.args)
        the_log.error(str(dt) + ": " + the_message + str(e.args[0]) + " " + proc)
        return "Error: " + mark_safe(the_message)
    except Exception as internal_e:
        the_log.error(str(dt) + ": " + str(internal_e.args) + ", " + str(internal_e.args[0]) + " " + proc)
        return "There was an error while handling an application exception. Contact your administrator."


def update_cache_log(msg):
    val = False
    try:
        file_loc = str(BASE_DIR / 'cache.log')
        log = open(file_loc, 'a', newline=None)
        log.write(str(datetime.datetime.now()) + ": " + msg)
        log.close()
        val = True
        return val
    except Exception as e:
        catch_err(e, 'wd_utils.update_cache_log')
        return val
