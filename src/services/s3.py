import aioboto3
from aiobotocore.config import AioConfig
from furl import furl


async def upload_html_s3(html_code: str, settings, filename: str = "index.html"):
    session = aioboto3.Session()
    config = AioConfig(
        max_pool_connections=settings.s3.max_connections,
        connect_timeout=settings.s3.connect_timeout,
        read_timeout=settings.s3.read_timeout,
    )
    async with session.client(
        "s3",
        endpoint_url=str(settings.s3.endpoint_url),
        aws_access_key_id=settings.s3.access_key.get_secret_value(),
        aws_secret_access_key=settings.s3.secret_key.get_secret_value(),
        config=config,
    ) as client:
        await client.put_object(
            Bucket=settings.s3.bucket,
            Key=filename,
            Body=html_code.encode("utf-8"),
            ContentType="text/html",
            ContentDisposition="inline",
        )


async def upload_screen_s3(screenshot_bytes, settings, filename: str = "index.png"):
    session = aioboto3.Session()
    config = AioConfig(
        max_pool_connections=settings.s3.max_connections,
        connect_timeout=settings.s3.connect_timeout,
        read_timeout=settings.s3.read_timeout,
    )
    async with session.client(
        "s3",
        endpoint_url=str(settings.s3.endpoint_url),
        aws_access_key_id=settings.s3.access_key.get_secret_value(),
        aws_secret_access_key=settings.s3.secret_key.get_secret_value(),
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
    endpoint = str(settings.s3.endpoint_url).rstrip("/")
    base = furl(f"{endpoint}/{settings.s3.bucket}/{filename}")
    view_url = str(base)
    download = base.copy()
    download.args["response-content-disposition"] = "attachment"
    screenshot_url = f"{endpoint}/{settings.s3.bucket}/{screen}"
    return view_url, str(download), screenshot_url
