from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse




import asyncio
import time
import random


app = FastAPI(title="Мой первый API", version="1.0")

@app.get("/", response_class=HTMLResponse)
async def get_page():
    await asyncio.sleep(0.5)
    return "<h1>Hello      Worrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrld!!!</h1>"

@app.get("/json")
async def get_json_data():


    await asyncio.sleep(0.5)
    return {"message": "Это ответ в JSON"}

@app.get("/info")
async def get_json_info():
    await asyncio.sleep(0.5)
    return{"company_name": "Рога и копыта", "company_address": "Улица пушкина, дом 12"
    }


@app.get("/count")
async def count_stream():
    async def generate_count():
        while True:
            yield f"{random.randint(0, 100)}\n"
            await asyncio.sleep(0.5)
    return StreamingResponse(generate_count(), media_type="text/html"
    )