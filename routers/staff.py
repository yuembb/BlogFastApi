from datetime import datetime, timedelta

import jwt
from cryptography.fernet import Fernet
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from psycopg2.extras import Json
from pydantic import BaseModel
from starlette.requests import Request
from starlette.responses import JSONResponse

from base_engine import create_db_session, Fernet_Key_Staff, Access_Token_Expire_Minutes_Staff, Secret_Key_Staff
from functions import fetchone__dict2dot, connection_close, create_or_update_access_token_staff, token_check, commit__connection_close, fetchall__dict2dot

router = APIRouter()

class Staff(BaseModel):
    content: dict = {
        "id": 0,
        "fullname": "",
        "email": "",
        "password": "",
        "can_create_category": False,
        "can_create_article": False,
        "can_create_staff": False,
    }

class CreateStaff(BaseModel):
    content: dict = {
        "name": "",
        "surname": "",
        "email": "",
        "password": ""
    }

class StaffUpdate(BaseModel):
    content: dict = {
        "name": "",
        "surname": "",
        "email": "",
        "password": ""
    }


@router.post("/login", summary="Login" )
def staff_login(request: Request, form: OAuth2PasswordRequestForm = Depends()):
    connection, cursor = create_db_session()

    time_now = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S.%f")
    staff_info = fetchone__dict2dot(cursor, f"select * from staffs where content ->> 'email' = '{form.username}';")

    if not staff_info:
        connection_close(connection, cursor)
        return JSONResponse(status_code=400, content={'status': 'incorrect_username_or_password'})

    if not Fernet(Fernet_Key_Staff).decrypt(str(staff_info.content["password"]).encode()).decode() == form.password:
        connection_close(connection, cursor)
        return JSONResponse(status_code=401, content={'status': 'password_is_wrong'})

    staff_id = staff_info.id
    email = staff_info.content["email"]

    last_token = fetchone__dict2dot(cursor, f"select * from staff_tokens where content ->> 'staff_id' = '{staff_id}' ORDER BY id desc ;")

    if last_token:
        time_diff_minutes = (datetime.strptime(time_now, "%Y-%m-%d %H:%M:%S.%f") - datetime.strptime(last_token.content["created_time"], "%Y-%m-%d %H:%M:%S.%f")).seconds / 60

        if Access_Token_Expire_Minutes_Staff > time_diff_minutes:
            access_token = last_token.content["access_token"]
            jwt.decode(access_token, Secret_Key_Staff, options={"verify_signature": False, 'verify_exp': False})
        else:
            expire = datetime.strptime(time_now, "%Y-%m-%d %H:%M:%S.%f") + timedelta(minutes=Access_Token_Expire_Minutes_Staff)
            access_token = create_or_update_access_token_staff(data={"time": time_now, "exp": expire, "expire": str(expire), "email": email})

            try:
                access_token = access_token.decode('utf-8')
            except:
                pass
            content = {"staff_id": staff_id, "last_token": last_token.content["access_token"], "access_token": access_token, "created_time": time_now}

            cursor.execute(f'''insert into staff_tokens (content,insert_time) values ({Json(content)},'{datetime.now()}');''')
            connection.commit()
    else:
        expire = datetime.strptime(time_now, "%Y-%m-%d %H:%M:%S.%f") + timedelta(minutes=Access_Token_Expire_Minutes_Staff)
        access_token = create_or_update_access_token_staff(data={"time": time_now, "exp": expire, "expire": str(expire), "email": email})
        try:
            access_token = access_token.decode('utf-8')
        except:
            pass
        content = {"staff_id": staff_id, "last_token": '', "access_token": access_token, "created_time": time_now}
        cursor.execute(f'''insert into staff_tokens (content) values ({Json(content)});''')
        connection.commit()

    content = {"staff_id": staff_id, "ip_address": request.client.host, "login_when": time_now}
    cursor.execute(f'''insert into staff_api_logins (content) values ({Json(content)});''')
    connection.commit()
    connection_close(connection, cursor)
    return {"access_token": access_token, 'staff_id': staff_id}


@router.post("/create", summary="Yazar Oluşturma")
def create_staff( record_info: CreateStaff, check_staff: Staff = Depends(token_check)):
    ###################################################################
    customer_staff, connection, cursor = check_staff
    if not customer_staff: return JSONResponse(status_code=401, content={'status': False, 'message': 'staff_not_found'})
    ###################################################################
    content = record_info.content

    check_record = fetchone__dict2dot(cursor, f'''select * from staffs where content ->> 'email' = '{content['email']}';''')
    if check_record:
        connection_close(connection, cursor)
        return {"status": "staff_exist"}

    content["password"] = Fernet(Fernet_Key_Staff).encrypt(str(content["password"]).encode()).decode()

    cursor.execute(f'''insert into staffs (content) values ({Json(content)});''')
    commit__connection_close(connection, cursor)

    return {'status': 'created'}

@router.get("/gets",summary="get staffs")
def gets_staff(check_staff:Staff=Depends(token_check)):
    customer_staff, connection, cursor = check_staff
    if not customer_staff: return JSONResponse(status_code=401, content={'status': False, 'message': 'staff_not_found'})

    staffs = fetchall__dict2dot(cursor,f'''select * from staffs;''')
    if staffs:
        return staffs

    connection_close(connection,cursor)
    return {"status":"staff_not_found"}

@router.get("/get",summary="get staffs")
def gets_staff(staff_id:int,check_staff:Staff=Depends(token_check)):
    customer_staff, connection, cursor = check_staff
    if not customer_staff: return JSONResponse(status_code=401, content={'status': False, 'message': 'staff_not_found'})

    staffs = fetchone__dict2dot(cursor,f'''select * from staffs where id={staff_id} ;''')
    if staffs:
        return staffs

    connection_close(connection,cursor)
    return {"status":"staff_not_found"}


@router.put("/update",summary="post staff")
def update_staff(staff_id:int,staff_info:StaffUpdate,check_staff:Staff=Depends(token_check)):
    customer_staff, connection, cursor = check_staff
    if not customer_staff: return JSONResponse(status_code=401, content={'status': False, 'message': 'staff_not_found'})

    check_record = fetchone__dict2dot(cursor,f'''select * from staffs where id = {staff_id}   ;''')
    if not check_record:
        connection_close(connection,cursor)
        return {"status":"staff_not_found"}

    incoming_data = staff_info.content

    new_staff_data = check_record.content
    new_staff_data["name"]= incoming_data["name"]
    new_staff_data["surname"]= incoming_data["surname"]
    new_staff_data["email"]= incoming_data["email"]
    new_staff_data["password"]= incoming_data["password"]
    new_staff_data["password"] = Fernet(Fernet_Key_Staff).encrypt(str(new_staff_data["password"]).encode()).decode()

    cursor.execute(f'''update staffs set content= ({Json(new_staff_data)}) where id={staff_id}   ;''')
    commit__connection_close(connection,cursor)
    return {"status":"updated"}