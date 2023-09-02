import os
import zipfile
import importlib
import markdown
import uvicorn

from fastapi import FastAPI, Request, UploadFile

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse

from pywebio.platform.fastapi import webio_routes

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


def install_projects() -> None:
    project_list = os.listdir('projects')

    for project in project_list:
        module = importlib.import_module(f'projects.{project}.main')

        if (os.path.isfile(f'./projects/{project}/requirements.txt')):
            os.system(
                f'cat ./projects/{project}/requirements.txt | xargs poetry add')

        if hasattr(module, 'subapp'):
            app.mount(f"/{project}", module.subapp)
        else:
            app.mount(f"/{project}", FastAPI(routes=webio_routes(module.main)))


install_projects()


@app.post("/projects")
async def upload_project(upload_file: UploadFile) -> JSONResponse:
    try:
        with open(f'./tmp/{upload_file.filename}', 'wb') as binary_file:
            binary_file.write(upload_file.file.read())

        with zipfile.ZipFile(f'./tmp/{upload_file.filename}', 'r') as zip_file:
            zip_file.extractall('./projects/')

        os.remove(f'./tmp/{upload_file.filename}')

        install_projects()

        return JSONResponse(status_code=200, content={"status": 200, "msg": "Проект успешно установлен. Обновите страницу, чтобы увидеть свой проект в спике"})
    except:
        return JSONResponse(status_code=500, content={"status": 500, "msg": "Во время установки проекта произошла ошибка"})


@app.get("/")
def read_main(request: Request):

    project_descs = []
    project_list = os.listdir('projects')

    for project in project_list:
        with open(f'projects/{project}/desc.md', 'r', encoding='utf-8') as f:
            desc = markdown.markdown(f.read())
            project_descs.append({
                'name': project,
                'desc': desc
            })

    return templates.TemplateResponse("home.html", {"request": request, "projects": project_descs})


if __name__ == '__main__':
    uvicorn.run(app='main:app', reload=True)
