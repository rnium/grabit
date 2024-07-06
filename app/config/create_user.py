import sys
from pathlib import Path
app_root = Path.cwd().parent.parent
sys.path.append(str(app_root))

from app.crud.users import create_user
from app.config.database import SessionLocal



def perform_create():
    try:
        name = sys.argv[1]
        username = sys.argv[2]
        password = sys.argv[3]
    except IndexError:
        print("Missing arguments")
        return
    if len(name) < 3  or len(username) < 3 or len(password) < 6:
        raise ValueError('Minimum length not met!')
    else:
        with SessionLocal() as db:
            create_user(db, {'username': username, 'name': name, 'password': password})
        print('User created')
        # print({'usename': username, 'name': name, 'password': password})

if __name__ == '__main__':
    perform_create()