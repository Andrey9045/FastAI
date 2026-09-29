from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from html_page_generator import AsyncDeepseekClient, AsyncUnsplashClient

from env_settings import AppSettings
from routers import sites, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Приложение стартует")
    settings = AppSettings()
    async with (
        AsyncUnsplashClient.setup(settings.unsplash.api_key.get_secret_value(), timeout=settings.unsplash.timeout),
        AsyncDeepseekClient.setup(
            settings.deepseek.api_key.get_secret_value(),
            str(settings.deepseek.base_url),
            settings.deepseek.model
        )
    ):
        app.state.settings = settings
        yield
    print("Приложение останавливается...")


app = FastAPI(lifespan=lifespan, title="My FastAI", description="API для генерации")
app.include_router(users.router)
app.include_router(sites.router)

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
