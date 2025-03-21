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
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

limiter = Limiter(key_func=get_remote_address,
                  storage_uri="redis://localhost:6379/0")
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


update_key = 'update_key' # should be changed, will be moved to .env
update_url = 'update' # should be changed, will be moved to .env


class TriggerUpdate(BaseModel):
    key: str


@app.post(f"/trigger-update/{update_url}")
async def trigger_fetch(t: TriggerUpdate, background_tasks: BackgroundTasks):
    if t.key != update_key:
        return JSONResponse(status_code=400, content={"message": "Invalid Key"})

    background_tasks.add_task(cron_job)
    return {"message": "Success"}


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
                            dependencies=[Depends(check_rate_limit)])

app.include_router(router=graphql_app, prefix='/graphql')


@app.get("/")
async def root():
    return {"message": "test"}
