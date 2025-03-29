import os
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



schema = strawberry.federation.Schema(query=Query)




limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@limiter.limit("60/minute")
async def check_rate_limit(request: Request):
    return True


@app.exception_handler(RateLimitExceeded)
async def rate_limit_exception(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "message":
                "Rate limit exceeded. "
                f"Please try again in {int(exc.limit.limit.get_expiry() / 60)} mins",
        })


graphql_app = GraphQLRouter(schema=schema,
                            graphiql=False,
                            dependencies=[Depends(check_rate_limit)])

app.include_router(router=graphql_app, prefix='/graphql/v1/city_insights')
