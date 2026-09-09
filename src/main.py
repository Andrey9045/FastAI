import asyncio
from datetime import datetime
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints
from pydantic.alias_generators import to_camel

MEDIA_DIR = Path(__file__).parent / "media"
app = FastAPI(title="My FastAI", description="API для генерации")

SiteTitle = Annotated[str, StringConstraints(max_length=100)]


class UserProfile(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        json_schema_extra={
            "examples": [
                {
                    "email": "example@example.com",
                    "isActive": True,
                    "profileId": "1",
                    "registeredAt": "2025-06-15T18:29:56+00:00",
                    "updatedAt": "2025-06-15T18:29:56+00:00",
                    "username": "user123"
                }
            ]
        })
    email: EmailStr
    is_active: Annotated[bool, "Авторизованный/Неавторизованный пользователь"]
    profile_id: Annotated[str, "ID профиля"]
    registered_at: Annotated[datetime, "Время регистрации"]
    updated_at: Annotated[datetime, "Время обновления"]
    username: Annotated[str, StringConstraints(max_length=20)]


class CreateSiteRequest(BaseModel):
    prompt: Annotated[str, "Промт"]


class GenerateHTMLRequest(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        json_schema_extra={
            "examples": [
                {
                    "prompt": "Сайт любителей играть в домино",
                }
            ]
        })
    prompt: Annotated[str, "Промт"]


class CreateSiteResponse(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        json_schema_extra={
            "examples": [
                {
                    "createdAt": "2025-06-15T18:29:56+00:00",
                    "htmlCodeDownloadUrl": "http://127.0.0.1:8000/media/index.html?response-content-disposition=attachment",
                    "htmlCodeUrl": "http://127.0.0.1:8000/media/index.html",
                    "id": 1,
                    "prompt": "Сайт любителей играть в домино",
                    "screenshotUrl": "/media/index.png",
                    "title": "Фан клуб Домино",
                    "updatedAt": "2025-06-15T18:29:56+00:00"
                }
            ]
        })
    created_at: Annotated[datetime, "Время создания"]
    html_code_download_url: SiteTitle
    html_code_url: SiteTitle
    id: Annotated[int, Field(gt=0, description="ID сайта")]
    prompt: Annotated[str, "Промт"]
    screenshot_url: SiteTitle
    title: Annotated[str, "Заголовок"]
    updated_at: Annotated[datetime, "Время обновления"]


class SitesListResponse(BaseModel):
    sites: list[CreateSiteResponse]


@app.get(
    "/frontend-api/users/me",
    response_model=UserProfile,
    summary="Получить информацию о пользователе",
    response_description="Пользователь"
)
def mock_authorized_user():
    mock_user_data = {
        "email": "example@example.com",
        "isActive": True,
        "profileId": "1",
        "registeredAt": "2025-06-15T18:29:56+00:00",
        "updatedAt": "2025-06-15T18:29:56+00:00",
        "username": "user123"
    }

    return UserProfile.model_validate(mock_user_data)


@app.get("/frontend-api/sites/my", response_model=SitesListResponse, summary="Список сайтов пользователя")
def mock_my_sites():
    return SitesListResponse(
        sites=[
            {
                "createdAt": "2025-06-15T18:29:56+00:00",
                "htmlCodeDownloadUrl": "/media/download/index.html",
                "htmlCodeUrl": "/media/index.html",
                "id": 1,
                "prompt": "Сайт любителей играть в домино",
                "screenshotUrl": "/media/index.png",
                "title": "Фан клуб Домино",
                "updatedAt": "2025-06-15T18:29:56+00:00"
            }
        ]
    )


@app.get(
    "/frontend-api/sites/{site_id}",
    response_model=CreateSiteResponse,
    summary="Получить сайт",
    response_description="Сайт по ID"
)
def mock_get_site(site_id: int):
    mock_site_data = {
        "createdAt": "2025-06-15T18:29:56+00:00",
        "htmlCodeDownloadUrl": "http://127.0.0.1:8000/media/index.html?response-content-disposition=attachment",
        "htmlCodeUrl": "http://127.0.0.1:8000/media/index.html",
        "id": site_id,
        "prompt": "Сайт любителей играть в домино",
        "screenshotUrl": "https://google.com",
        "title": "Фан клуб Домино",
        "updatedAt": "2025-06-15T18:29:56+00:00"
    }
    return CreateSiteResponse.model_validate(mock_site_data)


@app.post(
    "/frontend-api/sites/create",
    response_model=CreateSiteResponse,
    summary="Информация о созданном сайте",
    response_description="Создать сайт"
)
def mock_create_site(request: CreateSiteRequest):
    mock_site_data = {
        "createdAt": "2025-06-15T18:29:56+00:00",
        "htmlCodeDownloadUrl": "http://127.0.0.1:8000/media/index.html?response-content-disposition=attachment",
        "htmlCodeUrl": "http://127.0.0.1:8000/media/index.html",
        "id": 1,
        "prompt": request.prompt,
        "screenshotUrl": "https://google.com",
        "title": "dfgdfssdfh",
        "updatedAt": "2025-06-15T18:29:56+00:00"
    }
    return CreateSiteResponse.model_validate(mock_site_data)


async def generate_chunks(file_path, chunk_size: int = 256):
    if not file_path.exists():
        raise HTTPException(status_code=400, detail="Invalid file paath")
    with open(file_path, encoding="utf-8") as file:
        while chunk := file.read(chunk_size):
            await asyncio.sleep(0.1)
            yield chunk


@app.post(
    "/frontend-api/sites/{site_id}/generate",
    summary="Трансляция сайта по мере генерации",
    response_description="Генерация сайта"
)
async def mock_generate_site(site_id: int, request: GenerateHTMLRequest):
    file_path = Path(__file__).parent / "media" / "index.html"
    return StreamingResponse(
        content=generate_chunks(file_path, chunk_size=256),
        media_type="text/plain; charset=utf-8"
    )


app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
