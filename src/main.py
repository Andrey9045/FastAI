import asyncio
import time
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Annotated

import aioboto3
import anyio
import httpx
from aiobotocore.config import AioConfig
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from furl import furl
from gotenberg_api import GotenbergServerError, ScreenshotHTMLRequest
from html_page_generator import AsyncDeepseekClient, AsyncPageGenerator, AsyncUnsplashClient
from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints
from pydantic.alias_generators import to_camel

from env_settings import AppSettings


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


async def upload_html_s3(html_code: str, settings, filename: str = "index.html"):
    session = aioboto3.Session()
    config = AioConfig(
        max_pool_connections=settings.s3.max_pool_connections,
        connect_timeout=settings.s3.connect_timeout,
        read_timeout=settings.s3.read_timeout,
    )
    async with session.client(
        "s3",
        endpoint_url=settings.s3.endpoint_url,
        aws_access_key_id=settings.s3.access_key,
        aws_secret_access_key=settings.s3.secret_key,
        config=config,
    ) as client:
        await client.put_object(
            Bucket=settings.s3.bucket,
            Key=filename,
            Body=html_code.encode("utf-8"),
            ContentType="text/html",
            ContentDisposition="inline",
        )


async def take_screenshot(html_code: str, settings):
    try:
        async with httpx.AsyncClient(
            base_url=settings.gotenberg.url,
            timeout=settings.gotenberg.timeout,
        ) as client:
            screenshot_bytes = await ScreenshotHTMLRequest(
                index_html=html_code,
                width=settings.gotenberg.width,
                format=settings.gotenberg.format,
                wait_delay=settings.gotenberg.wait_delay,
            ).asend(client)
        return screenshot_bytes
    except GotenbergServerError as e:
        print(f"Screenshot error: {e}")
        return None


async def upload_screen_s3(screenshot_bytes, settings, filename: str = "index.png"):
    session = aioboto3.Session()
    config = AioConfig(
        max_pool_connections=settings.s3.max_pool_connections,
        connect_timeout=settings.s3.connect_timeout,
        read_timeout=settings.s3.read_timeout,
    )
    async with session.client(
        "s3",
        endpoint_url=settings.s3.endpoint_url,
        aws_access_key_id=settings.s3.access_key,
        aws_secret_access_key=settings.s3.secret_key,
        config=config,
        ) as client:
        await client.put_object(
            Bucket=settings.s3.bucket,
            Key=filename,
            Body=screenshot_bytes,
            ContentType="image/png",
            ContentDisposition="inline",
        )


def get_site_urls(settings, filename: str = "index.html", screen: str = "index.png"):
    base = furl(f"{settings.s3.endpoint_url}/{settings.s3.bucket}/{filename}")
    view_url = str(base)
    download = base.copy()
    download.args["response-content-disposition"] = "attachment"
    screenshot_url = f"{settings.s3.endpoint_url}/{settings.s3.bucket}/{screen}"
    return view_url, str(download), screenshot_url


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
def mock_my_sites(http_request: Request):
    last = getattr(http_request.app.state, "last_generated", {})
    view_url, download_url, screenshot_url = get_site_urls(http_request.app.state.settings)
    return SitesListResponse(
        sites=[
            {
                "createdAt": last.get("created_at", "2025-06-15T18:29:56+00:00"),
                "htmlCodeDownloadUrl": download_url,
                "htmlCodeUrl": view_url,
                "id": 1,
                "prompt": last.get("prompt", "Не сгенерирован"),
                "screenshotUrl": screenshot_url,
                "title": last.get("title", "Без названия"),
                "updatedAt": last.get("updated_at", "2025-06-15T18:29:56+00:00")
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
    view_url, download_url, screenshot_url = get_site_urls(http_request.app.state.settings)

    mock_site_data = {
        "createdAt": last.get("created_at", "Вовремя"),
        "htmlCodeDownloadUrl": download_url,
        "htmlCodeUrl": view_url,
        "id": site_id,
        "prompt": last.get("prompt", "Сайт не сгенерирован"),
        "screenshotUrl": screenshot_url,
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
def mock_create_site(request: CreateSiteRequest, http_request: Request):
    last = getattr(http_request.app.state, "last_generated", {})
    view_url, download_url, screenshot_url = get_site_urls(http_request.app.state.settings)
    mock_site_data = {
        "createdAt": "2025-06-15T18:29:56+00:00",
        "htmlCodeDownloadUrl": download_url,
        "htmlCodeUrl": view_url,
        "id": 1,
        "prompt": request.prompt,
        "screenshotUrl": screenshot_url,
        "title": last.get("title", "Новый сайт"),
        "updatedAt": last.get("updated_at", "2025-06-15T18:29:56+00:00")
    }
    return CreateSiteResponse.model_validate(mock_site_data)


async def generate_chunks(prompt: str, debug: bool, request: Request):
    generator = AsyncPageGenerator(debug_mode=debug)
    with anyio.CancelScope(shield=True):
        try:
            async for chunk in generator(prompt):
                yield chunk
        except asyncio.CancelledError:
            print("Клиент отключился, продолжается генерация")
        except Exception as e:
            yield f"\n[ОШИБКА] {type(e).__name__}: {e}\n"
            return
        await upload_html_s3(generator.html_page.html_code, request.app.state.settings)
        screenshot_bytes = await take_screenshot(
            generator.html_page.html_code,
            request.app.state.settings,
        )
        if screenshot_bytes:
            await upload_screen_s3(
                screenshot_bytes,
                request.app.state.settings,
            )
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


app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
