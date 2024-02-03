from cryptography.fernet import Fernet
import os
import secrets
import string
from django.utils.encoding import force_str
from pathlib import Path
import datetime


def get_django_key():
    """retrieves the django secret key needed at runtime. Location is stored in environment variable. If
    variable not set or file is inaccessible, function generates a fallback random key."""
    c = string.ascii_letters + string.digits + string.punctuation
    fallback_key = ''.join(secrets.choice(c) for i in range(32))
    app_dir = Path(__file__).resolve().parent.parent
    # todo: update oredev, oreback & ore.
    try:
        path = os.environ.get('DJANGO_KEY')
        if path is None:
            raise Exception('Server was not able to open DJANGO_KEY file.')
        else:
            with open(path, 'r') as django_key:
                key = django_key.read()
                return key
    except Exception as e:
        file_loc = str(app_dir / 'issue.log')
        log = open(file_loc, 'a', newline='\n')
        log.write('\n' + str(datetime.datetime.now()) + " keytrieve.getdjangokey " + str(e.args[0]))
        log.close()
        return fallback_key
