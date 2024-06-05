from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

from routers import staff, blog, category

# endregion

# region App
app = FastAPI(docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
# endregion

# region Routers
app.include_router(staff.router, tags=['1 - Staffs'], prefix='/staff')
app.include_router(category.router, tags=['2- Category'], prefix='/category')
app.include_router(blog.router, tags=['3- Blog'], prefix='/blog')


# endregion

# region Custom Open Api
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    from fastapi.openapi.utils import get_openapi
    openapi_schema = get_openapi(title="Deneme Project", version="0.0.0.1", description="Emirhan First Project", routes=app.routes)
    openapi_schema["info"]["x-logo"] = {"url": "/static/favicon.png"}
    app.openapi_schema = openapi_schema
    return app.openapi_schema


#########################################
@app.get("/", include_in_schema=False)
async def homepage():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="First Project",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
        swagger_favicon_url="/static/favicon.png")


# endregion
app.openapi = custom_openapi
