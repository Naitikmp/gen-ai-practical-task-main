import logging_config
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from core.config import settings
from core import config
import os
import sys
from langgraph_workflow.routes import router as langgraph_workflow_router

SHOW_DOCS_ENVIRONMENT = ("local")  # explicit list of allowed envs

logger = logging.getLogger(__name__)

# set url for swagger docs as null if api is not public
openapi_url="/api/openapi.json" if settings.ENVIRONMENT in SHOW_DOCS_ENVIRONMENT else None
    
# Initialize FastAPI app
app = FastAPI(
    title="Gaming Agent",
    openapi_url=openapi_url
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure templates
templates = Jinja2Templates(directory="templates")

########################## Define Routers ########################## 
module_api_path = "/api/v1"
app.include_router(langgraph_workflow_router, prefix=module_api_path)

########################## WEB UI (HTML) ##########################
# Home route 
@app.get("/", name="redirect-home")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# game route 
@app.get("/game", name="game-home")
async def game(request: Request):
    return templates.TemplateResponse("game.html", {"request": request})

########################## Main ##########################
if __name__ == "__main__":
    try:
        import uvicorn
        logger.info("Starting Uvicorn server...")
        reload = True if (settings.ENVIRONMENT == "local") else False
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=reload)
    except KeyboardInterrupt:
        logger.info("Server shutting down...")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
