import asyncio
import time
from datetime import UTC, datetime

import anyio
from fastapi import Request
from html_page_generator import AsyncPageGenerator

from services.gotenberg import take_screenshot
from services.s3 import upload_html_s3, upload_screen_s3


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
        now = datetime.now(UTC).isoformat()
        request.app.state.last_generated = {
            "title": generator.html_page.title or "Без названия",
            "prompt": prompt,
            "created_at": now,
            "updated_at": now,
        }
        request.app.state.last_generation_ts = int(time.time())
