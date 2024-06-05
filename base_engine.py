# region Imports

import psycopg2
import psycopg2.extras

# endregion

# region Engine

user = 'postgres'
password = 'R2dxkf22'
host = 'localhost'
port = '5435'
db_name = "blogdb"


def create_db_session():
    connection_db = psycopg2.connect(database=db_name, user=user, password=password, host=host, port=port)
    cursor_db = connection_db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    return connection_db, cursor_db


# region Staff Fernet
token_url_staff = "/staff/login"
Fernet_Key_Staff = b'YDWyjuUJ2G-gLjK-VJ9fMh2A99WIZr-HZP1PiiYOGGc='
Secret_Key_Staff = '09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7'
Access_Token_Expire_Minutes_Staff = 600
# endregion
