from cryptography.fernet import Fernet
import os
import subprocess
from django.utils.encoding import force_str


def get_django_key():
    # decrypts the SECRET KEY value and returns it to settings.py during
    # application startup.
    # os.system("source /data/bin/.env")
    # os.system("cd /data/bin")
    # os.system("source .env")

    p = os.getenv('WDD_KEY')
    with open(p, 'rb') as wdd_key:
        key = wdd_key.read()

    fk = Fernet(key)

    h = os.getenv('DJANGO_ENC')
    with open(h, 'rb') as enc:
        encrypted = enc.read()

    the_key = fk.decrypt(encrypted)

    return force_str(the_key)

