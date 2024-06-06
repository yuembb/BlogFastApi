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
        "staff_id": 0,
        "created_date": date.today()
    }


class UpdateBlog(BaseModel):
    content: dict = {
        "category_id": 0,
        "title": "",
        "contents": "",
        "staff_id": 0,
        "created_date": date.today()
    }


@router.post("/post", summary="Blog Ekleme")
def add_blog(blog: CreateBlog, chekc_staff: Staff = Depends(token_check)):
    staff_check, connection, cursor = chekc_staff
    if not staff_check: return JSONResponse(status_code=401, content={"status": False, "message": "staff_not_found"})

    content = blog.content

    cursor.execute(f'''insert into blog (content) values ({Json(content)})  ;''')
    commit__connection_close(connection, cursor)
    return {"status": "created"}


@router.get("/gets", summary="blogları getirme")
def get_blogs(check_staff: Staff = Depends(token_check)):
    staff_check, connection, cursor = check_staff
    if not staff_check: return JSONResponse(status_code=401, content={"status": False, "message": "staff_not_found"})

    blogs = fetchall__dict2dot(cursor, f'''select * from blog;''')
    if blogs:
        return blogs
    connection_close(connection, cursor)
    return {"status": "blog_not_found"}


@router.get("/get", summary="blog getirme")
def get_blogs(blog_id: int, check_staff: Staff = Depends(token_check)):
    staff_check, connection, cursor = check_staff
    if not staff_check: return JSONResponse(status_code=401, content={"status": False, "message": "staff_not_found"})

    blogs = fetchone__dict2dot(cursor, f'''select * from blog where id ={blog_id} ; ''')
    if blogs:
        return blogs
    connection_close(connection, cursor)
    return {"status": "blog_not_found"}


@router.get("/get-id", summary="get kategori ids")
def get_blogs(category_id: int, check_staff: Staff = Depends(token_check)):
    staff_check, connection, cursor = check_staff
    if not staff_check: return JSONResponse(status_code=401, content={"status": False, "message": "staff_not_found"})
    blogs = fetchall__dict2dot(cursor, f'''
    select 
        b.content ->> 'title' as blog_title,
        b.content ->> 'contents' as blog_contents,
        b.content ->> 'created_date' as created_date,
        s.content ->> 'name' as author_name,
        s.content ->> 'surname' as author_surname,
        c.content ->> 'name' as category_name
    from blog b 
    inner join 
        staffs s on (b.content ->> 'staff_id')::int = s.id 
    inner join 
        category c on (b.content ->> 'category_id')::int = c.id
    where b.content ->> 'category_id' = '{category_id}'
    ''')

    if blogs:
        return blogs
    connection_close(connection, cursor)
    return {"status": "blog_not_found"}

@router.get("/list",summary="slug a göre listeleme")
def list_slug(category_slug:str,check_staff:Staff=Depends(token_check)):
    staff_check , connection,curosr = check_staff
    if not staff_check: return JSONResponse(status_code=401,content={'Status':False,"message":"staff_not_found"})

    check_record = fetchall__dict2dot(curosr,f'''
       select b.content ->> 'title' as blog_title,
              b.content ->> 'contents' as blog_content,
              b.content ->> 'created_date' as blog_created_date,
              c.content ->> 'name' as category_name,
              s.content ->> 'name' as author_name,
              s.content ->> 'surname' as author_surname,
              s.content ->> 'email' as author_email
       from blog b
       inner join 
       category c on (b.content ->>'category_id')::int = c.id
       
       inner join 
       staffs s on (b.content->> 'staff_id')::int = s.id
       
       where c.content ->> 'slug' like '{category_slug}%'
       ;''')

    if check_record:
        return check_record
    connection_close(connection,curosr)
    return {"status":"blog_not_found"}

@router.put("/update", summary="post staff")
def update_blog(blog_id: int, blog_info: UpdateBlog, check_staff: Staff = Depends(token_check)):
    customer_staff, connection, cursor = check_staff
    if not customer_staff: return JSONResponse(status_code=401, content={'status': False, 'message': 'staff_not_found'})

    check_record = fetchone__dict2dot(cursor, f'''select * from blog where id = {blog_id}   ;''')
    if not check_record:
        connection_close(connection, cursor)
        return {"status": "blog_not_found"}

    incoming_data = blog_info.content

    new_blog_data = check_record.content
    new_blog_data["category_id"] = incoming_data["category_id"]
    new_blog_data["title"] = incoming_data["title"]
    new_blog_data["contents"] = incoming_data["contents"]
    new_blog_data["staff_id"] = incoming_data["staff_id"]
    new_blog_data["created_date"] = incoming_data["created_date"]

    cursor.execute(f'''update blog set content= ({Json(new_blog_data)}) where id={blog_id}   ;''')
    commit__connection_close(connection, cursor)
    return {"status": "updated"}

@router.get("/list-date",summary="list for date")
def get_date_list(check_staff:Staff=Depends(token_check)):
    staff_check , connection,cursor = check_staff
    if not staff_check: return JSONResponse(status_code=401, content={"status":False,"message":"staff_not_found"})

    check_record = fetchall__dict2dot(cursor,f'''select * from blog order by content->>'created_date' ;''')
    if not check_record:
        return {"status":"blog_not_found"}

    for date in check_record:
        print(date)


