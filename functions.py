
# region Imports
import os
import random
import time
from datetime import datetime, timedelta

import jwt
from cryptography.fernet import Fernet
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from psycopg2.extras import Json

from base_engine import create_db_session, Access_Token_Expire_Minutes_Staff, Secret_Key_Staff, token_url_staff, Fernet_Key_Staff


# endregion

# region Create or Update Access Token

def create_or_update_access_token_staff(*, data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=Access_Token_Expire_Minutes_Staff)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, Secret_Key_Staff)
    return encoded_jwt


# endregion

# region Check Token Staff
def token_check(token: str = Depends(OAuth2PasswordBearer(tokenUrl=token_url_staff, scheme_name='customer_staff'))):
    connection, cursor = create_db_session()
    try:
        time_now = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S.%f")
        payload = jwt.decode(token, Secret_Key_Staff, options={"verify_signature": False})
        token_create_time = datetime.strptime(payload.get("time"), '%Y-%m-%d %H:%M:%S.%f')
        time_diff_minutes = (datetime.strptime(time_now, "%Y-%m-%d %H:%M:%S.%f") - token_create_time).seconds / 60
        if Access_Token_Expire_Minutes_Staff < time_diff_minutes: return False
        email: str = payload.get("email")

        cursor.execute(f"select * from staffs where content ->> 'email' = '{email}';")
        staff = Dict2Dot(cursor.fetchone())
        return staff, connection, cursor
    except:
        connection_close(connection, cursor)
        return False, False, False


# endregion



# region DB Connection Close
def commit__connection_close(connection, cursor):
    connection.commit()
    cursor.close()
    connection.close()


def connection_close(connection, cursor):
    cursor.close()
    connection.close()

# endregion

# region Fetch Operations
class Dict2Dot(dict):
    def __getattr__(self, key):
        if key in self:
            return self[key]
        else:
            raise AttributeError(f"'{self.__class__.__name__}' objesinde '{key}' anahtarı bulunamadı.")


def fetchone__dict2dot(cursor, sql):
    cursor.execute(sql)
    sql_result = cursor.fetchone()
    if sql_result:
        return Dict2Dot(sql_result)
    else:
        return None


def fetchall__dict2dot(cursor, sql):
    cursor.execute(sql)
    sql_result = cursor.fetchall()
    result_list = []
    if sql_result:
        for result in sql_result:
            new_result = Dict2Dot(result)
            result_list.append(new_result)
        return result_list
    else:
        return result_list


# endregion