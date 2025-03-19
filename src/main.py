from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
import strawberry
from schema import Query

app = FastAPI()
schema = strawberry.federation.Schema(query=Query)
graphql_app = GraphQLRouter(schema=schema)

app.include_router(router=graphql_app, prefix='/graphql')


@app.get("/")
async def root():
    return {"message": "test"}
