from datetime import UTC, datetime

from fastapi import APIRouter

from models import UserProfile

router = APIRouter(prefix="/frontend-api/users", tags=["users"])


@router.get(
    "/me",
    response_model=UserProfile,
    summary="Получить информацию о пользователе",
    response_description="Пользователь"
)
def mock_authorized_user():
    now = datetime.now(UTC)
    mock_user_data = {
        "email": "example@example.com",
        "isActive": True,
        "profileId": "1",
        "registeredAt": now,
        "updatedAt": now,
        "username": "user123"
    }

    return UserProfile.model_validate(mock_user_data)
