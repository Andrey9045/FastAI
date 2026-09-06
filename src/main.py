from datetime import datetime
from typing import Annotated

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, EmailStr, StringConstraints
from pydantic.alias_generators import to_camel

app = FastAPI(title="My FastAI", description="API для генерации")


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


@app.get("/frontend-api/users/me", summary="Получить информацию о пользователе", response_description="Пользователь")
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


app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
