import os
import logging
import redis

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI, Request, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware  # Add this import
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

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.from_url(redis_url)

limiter = Limiter(key_func=get_remote_address,
                  storage_uri=redis_url)
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, replace with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


update_key = 'update_key'  # should be changed, will be moved to .env
update_url = 'update'  # should be changed, will be moved to .env


class TriggerUpdate(BaseModel):
    key: str


# json parameters should be updated before triggering the update
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

app.include_router(router=graphql_app, prefix='/graphql/v1/city_insights')
