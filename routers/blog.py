from datetime import date

from fastapi import APIRouter, Depends
from psycopg2.extras import Json
from pydantic import BaseModel
from starlette.responses import JSONResponse

from functions import token_check, fetchone__dict2dot, connection_close, commit__connection_close, fetchall__dict2dot
from routers.staff import Staff

router = APIRouter()


class CreateBlog(BaseModel):
    content: dict = {
        "category_id": 0,
        "title": "",
        "contents": "",
        "staff_id":0,
        "created_date":date.today()
    }


@router.post("/post", summary="Blog Ekleme")
def add_author(blog: CreateBlog, chekc_staff: Staff = Depends(token_check)):
    staff_check, connection, cursor = chekc_staff
    if not staff_check: return JSONResponse(status_code=401, content={"status": False, "message": "staff_not_found"})

    content = blog.content

    check_record = fetchone__dict2dot(cursor, f'''select * from staff where content ->>'email'='{content['staff_id']}';''')
    if check_record:
        connection_close(connection, cursor)
        return {"status": "email_already_exist"}

    cursor.execute(f'''insert into author (content) values ({Json(content)})  ;''')
    commit__connection_close(connection,cursor)
    return {"status":"created"}




