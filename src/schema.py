import strawberry
from typing import List
from statistics import mean
from models import DemographicsModel, EmploymentRate, get_db

@strawberry.type
class DemographicSchema:
    description: str
    area: str
    value: float

@strawberry.type
class EmploymentSchema:
    description: str
    area: str
    value: float


@strawberry.type
class Query:

    @strawberry.field
    def demographics_by_area(self, area: str) -> List[DemographicSchema]:
        db = next(get_db())
        demographics = db.query(DemographicsModel).filter(DemographicsModel.area == area).all()
        return demographics


    @strawberry.field
    def employment_rate(self, area: str) -> EmploymentSchema:
        db = next(get_db())

        employment_rate_all = db.query(EmploymentRate).filter(EmploymentRate.area == area).all()
        e = [i.value for i in employment_rate_all]
        employment_rate_mean = mean(e)

        return EmploymentSchema(description="average employment rate", area=area, value=round(employment_rate_mean, 2))




schema = strawberry.Schema(query=Query)
