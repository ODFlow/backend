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
from strawberry.fastapi import GraphQLRouter

from fetchers.fetcher import run_all_fetchers
from schema import Query

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def cron_job():
    try:
        run_all_fetchers()
    except Exception as e:
        logger.error("Error %s", e)


scheduler = BackgroundScheduler()
scheduler.add_job(cron_job,
                  CronTrigger(month="1,7", day="1", hour="5", minute="0"),
                  id="data_update",
                  name="Update all data")

schema = strawberry.federation.Schema(query=Query)
graphql_app = GraphQLRouter(schema=schema)

app.include_router(router=graphql_app, prefix='/graphql')


@app.get("/")
async def root():
    return {"message": "test"}
