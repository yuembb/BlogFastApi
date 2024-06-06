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
class UpdateCategory(BaseModel):
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

@router.get("/gets",summary="get category")
def gets_category(check_staff:Staff=Depends(token_check)):
    customer_staff, connection, cursor = check_staff
    if not customer_staff: return JSONResponse(status_code=401, content={'status': False, 'message': 'staff_not_found'})

    category = fetchall__dict2dot(cursor,f'''select * from category;''')
    if category:
        return category

    connection_close(connection,cursor)
    return {"status":"staff_not_found"}

@router.get("/get",summary="get category")
def gets_category(staff_id:int,check_staff:Staff=Depends(token_check)):
    customer_staff, connection, cursor = check_staff
    if not customer_staff: return JSONResponse(status_code=401, content={'status': False, 'message': 'staff_not_found'})

    category = fetchone__dict2dot(cursor,f'''select * from category where id={staff_id} ;''')
    if category:
        return category

    connection_close(connection,cursor)
    return {"status":"staff_not_found"}

@router.get("/slug-list",summary="list slug")
def get_slug(chekc_staff:Staff=Depends(token_check)):
    staff_check , connection,cursor = chekc_staff
    if not staff_check: return JSONResponse(status_code=401, content={"status":False,"message":"staff_not_found"})

    slug_list =[]
    check_record = fetchall__dict2dot(cursor,f'''select * from category;''')
    if not check_record:
        return {"category_not_found"}


    for slug in check_record:
        slug_dict={
            "slug_name":slug.content["slug"]
        }
        slug_list.append(slug_dict)
    return slug_list


@router.put("/update",summary="update kategori")
def update_category(category_id:int,category_info:UpdateCategory,chekc_staff:Staff=Depends(token_check)):
    customer_staff, connection, cursor = chekc_staff
    if not customer_staff: return JSONResponse(status_code=401, content={'status': False, 'message': 'staff_not_found'})

    check_record = fetchone__dict2dot(cursor,f'''select * from category where id = {category_id}   ;''')
    if not check_record:
        connection_close(connection, cursor)
        return {"status": "category_not_found"}

    incoming_data = category_info.content

    category_new_data = check_record.content
    category_new_data["name"] = incoming_data["name"]
    category_new_data["slug"] = incoming_data["slug"]


    cursor.execute(f'''update category set content ={Json(category_new_data)} where id = {category_id}   ;''')
    commit__connection_close(connection,cursor)
    return {"status":"updated"}


@router.delete("/delete",summary="category silme")
def delete_category(category_id:int,check_staff:Staff=Depends(token_check)):
    staff_check , connection,cursor = check_staff
    if not staff_check: return JSONResponse(status_code=401, content={"status":False,"message":"staff_not_found"})

    check_record = fetchone__dict2dot(cursor,f'''select * from category;''')
    if not check_record:
        connection_close(connection,cursor)
        return {"status":"category_not_found"}

    cursor.execute(f'''delete from category where id ={category_id}    ;''')
    commit__connection_close(connection,cursor)
    return {"status":"deleted"}

