from fastapi import APIRouter, Request, status
from fastapi.templating import Jinja2Templates

router = APIRouter()
template = Jinja2Templates(directory="Views")



@router.get("/", status_code= status.HTTP_200_OK)
async def getHomePage(req: Request):
    return template.TemplateResponse("/Template/index.html", {"request": req})