from datetime import UTC, datetime

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from models import CreateSiteRequest, CreateSiteResponse, GenerateHTMLRequest, SitesListResponse
from services.s3 import get_site_urls
from services.site_generator import generate_chunks

router = APIRouter(prefix="/frontend-api/sites", tags=["sites"])


@router.get("/my", response_model=SitesListResponse, summary="Список сайтов пользователя")
def mock_my_sites(http_request: Request):
    last = getattr(http_request.app.state, "last_generated", {})
    view_url, download_url, screenshot_url = get_site_urls(http_request.app.state.settings)
    now = datetime.now(UTC)
    return SitesListResponse(
        sites=[
            {
                "createdAt": last.get("created_at", now),
                "htmlCodeDownloadUrl": download_url,
                "htmlCodeUrl": view_url,
                "id": 1,
                "prompt": last.get("prompt", "Не сгенерирован"),
                "screenshotUrl": screenshot_url,
                "title": last.get("title", "Без названия"),
                "updatedAt": last.get("updated_at", now)
            }
        ]
    )


@router.get(
    "/{site_id}",
    response_model=CreateSiteResponse,
    summary="Получить сайт",
    response_description="Сайт по ID",
)
def mock_get_site(site_id: int, http_request: Request):
    last = getattr(http_request.app.state, "last_generated", {})
    view_url, download_url, screenshot_url = get_site_urls(http_request.app.state.settings)
    now = datetime.now(UTC)
    mock_site_data = {
        "createdAt": last.get("created_at", now),
        "htmlCodeDownloadUrl": download_url,
        "htmlCodeUrl": view_url,
        "id": site_id,
        "prompt": last.get("prompt", "Сайт не сгенерирован"),
        "screenshotUrl": screenshot_url,
        "title": last.get("title", "Без названия"),
        "updatedAt": last.get("updated_at", now),
    }
    return CreateSiteResponse.model_validate(mock_site_data)


@router.post(
    "/create",
    response_model=CreateSiteResponse,
    summary="Информация о созданном сайте",
    response_description="Создать сайт"
)
def mock_create_site(request: CreateSiteRequest, http_request: Request):
    last = getattr(http_request.app.state, "last_generated", {})
    view_url, download_url, screenshot_url = get_site_urls(http_request.app.state.settings)
    now = datetime.now(UTC)
    mock_site_data = {
        "createdAt": last.get("created_at", now),
        "htmlCodeDownloadUrl": download_url,
        "htmlCodeUrl": view_url,
        "id": 1,
        "prompt": request.prompt,
        "screenshotUrl": screenshot_url,
        "title": last.get("title", "Новый сайт"),
        "updatedAt": last.get("updated_at", now)
    }
    return CreateSiteResponse.model_validate(mock_site_data)


@router.post(
    "/{site_id}/generate",
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
