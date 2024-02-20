from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from starlette.middleware.cors import CORSMiddleware

import os
from fastapi_sqlalchemy import DBSessionMiddleware
from fastapi_sqlalchemy import db

from app.api.errors.http_error import http_error_handler
from app.api.errors.validation_error import http422_error_handler
from app.api.routes import router as api_router
from app.core.config import (ALLOWED_HOSTS, API_PREFIX, DEBUG, PROJECT_NAME,
                             VERSION,DATABASE_URL)
#from app.core.events import create_start_app_handler, create_stop_app_handler
from app.core.metadata import tags_metadata


def get_application() -> FastAPI:
    #Define the information of the main app of FastAPI
    application = FastAPI(title=PROJECT_NAME, debug=DEBUG,
                          version=VERSION, openapi_tags=tags_metadata)

    # add cors policy
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # ALLOWED_HOSTS or
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    application.add_middleware(DBSessionMiddleware, db_url=str(DATABASE_URL))
    # add handlers for http protocol responses
    application.add_exception_handler(HTTPException, http_error_handler)
    application.add_exception_handler(
        RequestValidationError, http422_error_handler)

#inlude router fastapi
    application.include_router(api_router, prefix=API_PREFIX)

    return application


app = get_application()

"""
@app.get("/")
async def main():
    return [{"msg": "main"}]

"""