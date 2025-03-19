import strawberry
from typing import List
from statistics import mean
from models import DemographicsModel, EmploymentRate, TrafficAccidents, Education, get_db
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
    timeframe: str
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
    def demographics(self, area: str) -> List[DemographicSchema]:
        db = next(get_db())
        demographics = db.query(DemographicsModel).filter(
            DemographicsModel.area == area).all()

        return demographics

    @strawberry.field
    def unemployment_rate(self, area: str) -> List[EmploymentSchema]:
        db = next(get_db())
        unemployment_data = db.query(EmploymentRate).filter(
            EmploymentRate.area == area).all()

        yearly_data = {}
        description = "average unemployment rate"

        for i in unemployment_data:

            year = i.timeframe[:4]
            if not description:
                description = i.description
            if year not in yearly_data:
                yearly_data[year] = []

            yearly_data[year].append(i.value)

        res = []
        for year, val in yearly_data.items():
            avg_yearly_rate = round(mean(val), 2)
            res.append(
                EmploymentSchema(area=area,
                                 description=description,
                                 timeframe=year,
                                 value=avg_yearly_rate))

        return res

    @strawberry.field
    def traffic_accidents(self, area: str) -> List[TrafficAccidentsSchema]:
        db = next(get_db())
        traffic_accidents = db.query(TrafficAccidents).filter(
            TrafficAccidents.area == area).all()

        return traffic_accidents

    @strawberry.field
    def traffic_accidents_sum(self, area: str) -> List[TrafficAccidentsSchema]:
        db = next(get_db())
        traffic_accidents = (db.query(
            TrafficAccidents.area, TrafficAccidents.year,
            func.sum(TrafficAccidents.value)).filter(
                TrafficAccidents.area == area).group_by(TrafficAccidents.year))

        result = []
        for area, year, total in traffic_accidents:
            result.append(
                TrafficAccidentsSchema(
                    description="Total traffic accidents per year",
                    area=area,
                    year=year,
                    value=total))

        return result

    @strawberry.field
    def education(self, area: str) -> List[EducationSchema]:
        db = next(get_db())
        education = db.query(Education).filter(Education.area == area).all()

        return education


schema = strawberry.Schema(query=Query)
