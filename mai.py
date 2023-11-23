from fastapi import FastAPI, Request, File, UploadFile, Response, WebSocket
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.websockets import WebSocketDisconnect
import os
import re
import pymysql
from starlette.routing import Router
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import sys

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Database connection setup
connection = pymysql.connect(
    host='localhost',
    user='root',
    password='1234',
    db='test',
    cursorclass=pymysql.cursors.DictCursor
)

app.mount("/static", StaticFiles(directory=Path("static")), name="static")
app.mount("/crops", StaticFiles(directory="crops"), name="crops")

@app.get("/crops/{filename}")
async def serve_image(filename: str):
    image_path = f"crops/{filename}"
    return FileResponse(image_path)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/analytics", response_class=HTMLResponse)
async def analytics(request: Request):
    return templates.TemplateResponse("bi.html", {"request": request})

@app.get("/display", response_class=HTMLResponse)
async def display(request: Request):
    cursor = connection.cursor()
    
    sqlc = "SELECT COUNT(flag) FROM image_paths where flag=1"
    cursor.execute(sqlc)
    res = cursor.fetchone()
    if res is None:
        counter = 0
    else:
        counter = res['COUNT(flag)']

    cursor.execute("SELECT path FROM image_paths")
    image_paths = [row['path'].replace('\\', '/') for row in cursor.fetchall()]
    cursor.close()

    return templates.TemplateResponse(
        "display.html",
        {"request": request, "image_paths": image_paths, "counter": counter},
    )

@app.get("/details/{image_path}", response_class=HTMLResponse)
async def details(image_path: str, request: Request):
    match = re.search(r'(\d+)', image_path)
    if match:
        image_id = match.group(1)
    else:
        raise Exception('No image id in the path')

    cursor = connection.cursor()
    cursor.execute("SELECT * FROM image_paths WHERE id = %s", (image_id,))
    image = cursor.fetchone()
    return templates.TemplateResponse("details.html", {"request": request, "image": image})

@app.get("/crops/{filename}")
async def serve_static(filename: str):
    full_path = filename
    return FileResponse(full_path)

@app.post("/restart")
async def restart():
    # Perform any necessary cleanup or shutdown procedures.
    # Then restart the application.
    python_executable = sys.executable

# Define the command to restart the FastAPI application with uvicorn
    uvicorn_command = [
    python_executable,
    '-m',
    'uvicorn',
    'mai:app',
    '--reload',
]

# Use os.execl to restart the application
    os.execl(python_executable, *uvicorn_command)

@app.post("/video_feed", response_class=Response)
async def video_feed(frame: UploadFile):
    frame_data = await frame.read()
    # Process the frame as needed
    # Use WebSocket to send frame data

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        try:
            frame = await websocket.receive_text()
            # Process frame data
        except WebSocketDisconnect:
            break


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(main, host="0.0.0.0", port=8000)
