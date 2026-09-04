from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
def get_page():
    return "<h1>Hello world!!! I`m best programmer!!!</h1>"
