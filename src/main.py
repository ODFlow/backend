import logging
import redis

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI, Request, Depends, BackgroundTasks
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.responses import JSONResponse
import strawberry
from schema import Query

app = FastAPI()
schema = strawberry.federation.Schema(query=Query)
graphql_app = GraphQLRouter(schema=schema)

app.include_router(router=graphql_app, prefix='/graphql')


@app.get("/")
async def root():
    return {"message": "test"}
