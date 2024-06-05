from fastapi import APIRouter, Depends
from psycopg2.extras import Json
from pydantic import BaseModel
from starlette.responses import JSONResponse

from functions import token_check, fetchone__dict2dot, connection_close, commit__connection_close, fetchall__dict2dot
from routers.staff import Staff

router = APIRouter()


class CreateAuthor(BaseModel):
    content: dict = {
        "name": "",
        "surname": "",
        "email": ""
    }


@router.post("/post", summary="Yazar Ekleme")
def add_author(author: CreateAuthor, chekc_staff: Staff = Depends(token_check)):
    staff_check, connection, cursor = chekc_staff
    if not staff_check: return JSONResponse(status_code=401, content={"status": False, "message": "staff_not_found"})

    content = author.content
    check_record = fetchone__dict2dot(cursor, f'''select * from author where content ->>'email'='{content['email']}';''')
    if check_record:
        connection_close(connection, cursor)
        return {"status": "email_already_exist"}

    cursor.execute(f'''insert into author (content) values ({Json(content)})  ;''')
    commit__connection_close(connection,cursor)
    return {"status":"created"}



