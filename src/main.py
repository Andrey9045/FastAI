from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="My FastAI", description="API для генерации")


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
    return JSONResponse(content=mock_user_data, status_code=200)


app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
