from cryptography.fernet import Fernet
import os
import secrets
import string
from django.utils.encoding import force_str
from pathlib import Path
import datetime


def set_django_key(key_file_path=None):
    # generate a random string 32 characters long. This will be used as the
    # Django SECRET_KEY for the Wikiframe app.
    app_dir = Path(__file__).resolve().parent.parent
    try:
        if not key_file_path:
            key_file_path = os.environ['DJANGO_KEY']
        with open(key_file_path, 'r') as kfp:
            key_val = kfp.read()

        with open(app_dir / '.env', 'r') as e:
            lines = e.readlines()
            n = 0
            for line in lines:
                if line[:10] == 'SECRET_KEY':
                    new_val = 'SECRET_KEY={}'.format(key_val) + '\n'
                    del lines[n]
                n += 1
            lines.append(new_val)

        with open(app_dir / '.env', 'w') as e:
            e.writelines(lines)
            return True
    except Exception as e:
        file_loc = str(app_dir / 'issue.log')
        log = open(file_loc, 'a', newline='\n')
        log.write('\n' + str(datetime.datetime.now()) + " keytrieve.set_django_key " + str(e.args[0]))
        log.close()
        return False


def get_django_key_old():
    """retrieves the django secret key needed at runtime. Location is stored in environment variable. If
    variable not set or file is inaccessible, function generates a fallback random key."""
    c = string.ascii_letters + string.digits + string.punctuation
    fallback_key = ''.join(secrets.choice(c) for i in range(32))
    app_dir = Path(__file__).resolve().parent.parent
    # todo: update oredev, oreback & ore.
    try:
        path = os.environ.get('DJANGO_KEY')
        if path is None:
            raise Exception('Server was not able to access DJANGO_KEY environment variable.')
        else:
            with open(path, 'r') as django_key:
                key = django_key.read()
                return key
    except Exception as e:
        file_loc = str(app_dir / 'issue.log')
        log = open(file_loc, 'a', newline='\n')
        log.write('\n' + str(datetime.datetime.now()) + " keytrieve.get_django_key " + str(e.args[0]))
        log.close()
        return fallback_key
