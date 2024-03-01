import secrets
import string
from pathlib import Path
import datetime


def get_django_key():
    """Retrieves django key from file. If the key doesn't exist, generates a new one randomly."""
    app_dir = Path(__file__).resolve().parent.parent
    file_path = app_dir / 'util/.ref_key'
    if not file_path.exists():
        issue_file_loc = str(app_dir / 'issue.log')
        log = open(issue_file_loc, 'a', newline='\n')
        log.write('\n' + str(datetime.datetime.now()) + " keytrieve.get_django_key " +
                  'Key retrieval failed, using temp key.')
        log.close()
        c = string.ascii_letters + string.digits + string.punctuation
        return ''.join(secrets.choice(c) for i in range(50))
    else:
        with open(file_path, 'r') as r:
            return r.read()

