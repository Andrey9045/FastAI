import httpx
from gotenberg_api import GotenbergServerError, ScreenshotHTMLRequest


async def take_screenshot(html_code: str, settings):
    try:
        async with httpx.AsyncClient(
            base_url=str(settings.gotenberg.url),
            timeout=settings.gotenberg.timeout,
        ) as client:
            screenshot_bytes = await ScreenshotHTMLRequest(
                index_html=html_code,
                width=settings.gotenberg.width,
                format=settings.gotenberg.format,
                wait_delay=settings.gotenberg.wait_delay,
            ).asend(client)
        return screenshot_bytes
    except (GotenbergServerError, httpx.HTTPError) as e:
        print(f"Screenshot error: {e}")
        return None
