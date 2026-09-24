from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints
from pydantic.alias_generators import to_camel

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
