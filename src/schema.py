import strawberry
from typing import List
from statistics import mean
from models import DemographicsModel, EmploymentRate,TrafficAccidents , Education,  get_db
from sqlalchemy.sql import func

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
class TrafficAccidentsSchema:
    description: str
    area: str
    year: str
    value: int

@strawberry.type
class EducationSchema:
    description: str
    age: str
    area: str
    value: int




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



    @strawberry.field
    def traffic_accidents(self, area: str) -> List[TrafficAccidentsSchema]:
        db = next(get_db())
        traffic_accidents = db.query(TrafficAccidents).filter(TrafficAccidents.area == area).all()

        return traffic_accidents



    @strawberry.field
    def traffic_accidents_sum(self, area: str) -> List[TrafficAccidentsSchema]:
        db = next(get_db())
        traffic_accidents = (
        db.query(
            TrafficAccidents.area,
            TrafficAccidents.year,
            func.sum(TrafficAccidents.value)
                )
        .filter(TrafficAccidents.area == area)
        .group_by(TrafficAccidents.year)
        )

        result = []
        for area, year ,total in traffic_accidents:
            result.append(TrafficAccidentsSchema(description="Total traffic accidents per year", area=area,year=year, value=total))

        return result



    @strawberry.field
    def education(self, area: str) -> List[EducationSchema]:
        db = next(get_db())
        education = db.query(Education).filter(Education.area == area).all()

        return education



schema = strawberry.Schema(query=Query)
