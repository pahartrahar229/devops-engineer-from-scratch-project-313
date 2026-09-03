import os
from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI

from app.database import create_db_and_tables
from app.routers import links, redirect

sentry_dsn = os.environ.get('SENTRY_DSN')
if sentry_dsn:
    sentry_sdk.init(dsn=sentry_dsn, traces_sample_rate=1.0)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title='Link Shortener', lifespan=lifespan)

app.include_router(links.router)
app.include_router(redirect.router)


@app.get('/ping')
def ping():
    return 'pong'


if __name__ == '__main__':
    import uvicorn

    port = int(os.environ.get('PORT', 8080))
    uvicorn.run(app, host='0.0.0.0', port=port)