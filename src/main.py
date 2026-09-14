import asyncio
import time
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Annotated

import anyio
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from html_page_generator import AsyncDeepseekClient, AsyncPageGenerator, AsyncUnsplashClient
from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints
from pydantic.alias_generators import to_camel

from env_settings import AppSettings

MEDIA_DIR = Path(__file__).parent / "media"


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Приложение стартует")
    settings = AppSettings()
    async with (
        AsyncUnsplashClient.setup(settings.unsplash.api_key.get_secret_value(), timeout=settings.unsplash.timeout),
        AsyncDeepseekClient.setup(
            settings.deepseek.api_key.get_secret_value(),
            settings.deepseek.base_url,
            settings.deepseek.model
        )
    ):
        app.state.settings = settings
        yield
    print("Приложение останавливается...")


app = FastAPI(lifespan=lifespan, title="My FastAI", description="API для генерации")

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
    response_description="Сайт по ID",
)
def mock_get_site(site_id: int, http_request: Request):
    last = getattr(http_request.app.state, "last_generated", {})
    ts = getattr(http_request.app.state, "last_generation_ts", 0)

    mock_site_data = {
        "createdAt": last.get("created_at", "2025-06-15T18:29:56+00:00"),
        "htmlCodeDownloadUrl": "/media/download/index.html",
        "htmlCodeUrl": f"/media/index.html?v={ts}",
        "id": site_id,
        "prompt": last.get("prompt", "Сайт не сгенерирован"),
        "screenshotUrl": "/media/index.png",
        "title": last.get("title", "Без названия"),
        "updatedAt": last.get("updated_at", "2025-06-15T18:29:56+00:00"),
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
        "id": 37,
        "prompt": request.prompt,
        "screenshotUrl": "https://google.com",
        "title": "dfgdfssdfh",
        "updatedAt": "2025-06-15T18:29:56+00:00"
    }
    return CreateSiteResponse.model_validate(mock_site_data)


async def generate_chunks(prompt: str, debug: bool, request: Request):
    generator = AsyncPageGenerator(debug_mode=debug)
    try:
        async for chunk in generator(prompt):
            yield chunk
    except asyncio.CancelledError:
        print("Генерация прервана клиентом")
        raise
    except Exception as e:
        yield f"\n[ОШИБКА] {type(e).__name__}: {e}\n"
        return
    with anyio.CancelScope(shield=True):
        output_path = MEDIA_DIR / "index.html"
        output_path.write_text(generator.html_page.html_code, encoding="utf-8")
        request.app.state.last_generated = {
            "title": generator.html_page.title or "Без названия",
            "prompt": prompt,
            "created_at": "2025-06-15T18:29:56+00:00",
            "updated_at": "2025-06-15T18:29:56+00:00",
        }
        request.app.state.last_generation_ts = int(time.time())


@app.post(
    "/frontend-api/sites/{site_id}/generate",
    summary="Трансляция сайта по мере генерации",
    response_description="Генерация сайта"
)
async def mock_generate_site(site_id: int, payload: GenerateHTMLRequest, request: Request):
    prompt = payload.prompt.strip()
    settings = request.app.state.settings
    return StreamingResponse(
        content=generate_chunks(prompt, debug=settings.debug, request=request),
        media_type="text/plain; charset=utf-8"
    )


app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
