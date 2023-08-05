"""Maintains set of seven issue logs, one active and six historical. Should be run on a once-a-day timer."""
import os
from wikidataDiscovery.settings import BASE_DIR


def rotate_logs():
    # list files to rename
    log_files = ['issue.log', 'issue.log.1', 'issue.log.2', 'issue.log.3', 'issue.log.4', 'issue.log.5', 'issue.log.6']
    path = str(BASE_DIR) + '/'

    # check to see if older logs exist
    for f in log_files:
        p = path + f
        if not os.path.isfile(p):
            open(p, 'x')

    # rename issue.log.1 - .6
    for f in range(6, 0, -1):
        old_name = path + 'issue.log.' + str(f)
        new_name = path + 'issue.log.' + str(f + 1)
        os.rename(old_name, new_name)

    # rename active issue.log; create new issue.log
    old_issue = path + 'issue.log'
    new_issue = path + 'issue.log.1'
    os.rename(old_issue, new_issue)
    open(old_issue, 'x')

    # delete issue.log.7. Keeps log depth at 1 week.
    del_issue = path + 'issue.log.7'
    os.unlink(del_issue)
