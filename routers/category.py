from fastapi import APIRouter, Depends
from psycopg2.extras import Json
from pydantic import BaseModel
from starlette.responses import JSONResponse

from functions import token_check, fetchone__dict2dot, connection_close, commit__connection_close, fetchall__dict2dot
from routers.staff import Staff

router = APIRouter()


class CreateCategory(BaseModel):
    content: dict = {
        "name": "",
        "slug": ""
    }


@router.post("/post", summary="Kategori Ekleme")
def add_category(category: CreateCategory, chekc_staff: Staff = Depends(token_check)):
    staff_check, connection, cursor = chekc_staff
    if not staff_check: return JSONResponse(status_code=401, content={"status": False, "message": "staff_not_found"})

    content = category.content


    cursor.execute(f'''insert into category (content) values ({Json(content)})  ;''')
    commit__connection_close(connection,cursor)
    return {"status":"created"}




