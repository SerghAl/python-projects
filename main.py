import os
import zipfile
import importlib
import markdown
import uvicorn
import asyncio
import nest_asyncio

from fastapi import FastAPI, Request, UploadFile

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse

from pywebio.platform.fastapi import webio_routes

app_dir = os.path.dirname(
    os.path.abspath(__file__))

templates_path = os.path.join(app_dir, 'templates')
static_path = os.path.join(app_dir, 'static')
projects_path = os.path.join(app_dir, 'projects')
tmp_path = os.path.join(app_dir, 'tmp')

app = FastAPI()
app.mount("/static", StaticFiles(directory=static_path), name="static")

templates = Jinja2Templates(directory=templates_path)


async def install_projects() -> None:
    project_list = os.listdir(projects_path)

    for project in project_list:
        module = importlib.import_module(f'projects.{project}.main')
        req_file_path = os.path.join(
            projects_path, f'{project}/requirements.txt')

        if (os.path.isfile(req_file_path)):
            os.system(
                f'cat {req_file_path} | xargs poetry -C {app_dir} add')

        if hasattr(module, 'subapp'):
            app.mount(f"/{project}", module.subapp)
        else:
            app.mount(f"/{project}", FastAPI(routes=webio_routes(module.main)))


@app.post("/projects")
async def upload_project(upload_file: UploadFile) -> JSONResponse:
    upload_file_path = os.path.join(tmp_path, upload_file.filename)

    try:
        with open(upload_file_path, 'wb') as binary_file:
            binary_file.write(upload_file.file.read())

        with zipfile.ZipFile(upload_file_path, 'r') as zip_file:
            zip_file.extractall(projects_path)

        os.remove(upload_file_path)

        install_projects()

        return JSONResponse(status_code=200, content={"status": 200, "msg": "Проект успешно установлен. Обновите страницу, чтобы увидеть свой проект в спике"})
    except:
        return JSONResponse(status_code=500, content={"status": 500, "msg": "Во время установки проекта произошла ошибка"})


@app.get("/")
def read_main(request: Request):

    project_descs = []
    project_list = os.listdir(projects_path)

    for project in project_list:
        des_file_path = os.path.join(
            projects_path, f'{project}/desc.md')

        with open(des_file_path, 'r', encoding='utf-8') as f:
            desc = markdown.markdown(f.read())
            project_descs.append({
                'name': project,
                'desc': desc
            })

    return templates.TemplateResponse("home.html", {"request": request, "projects": project_descs})


async def main():
    asyncio.create_task(install_projects())

    config = uvicorn.Config(app)
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == '__main__':
    asyncio.run(main())
