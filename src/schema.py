# pylint: disable=R0903

from statistics import mean
from typing import List

import strawberry
from sqlalchemy.sql import func

from models import DemographicsModel, EmploymentRate, TrafficAccidents, Education, Income, get_db


@strawberry.type
class DemographicSchema:
    """
    Represents the schema for demographics information
    """

    description: str
    area: str
    value: float


@strawberry.type
class EmploymentSchema:
    """
        Represents the schema for employment information
    """

    description: str
    area: str
    timeframe: str
    value: float


@strawberry.type
class TrafficAccidentsSchema:
    """
        Represents the schema for Traffic Accidents information
    """

    description: str
    area: str
    year: str
    value: int


@strawberry.type
class EducationSchema:
    """
        Represents the schema for education information
    """

    description: str
    age: str
    area: str
    value: int

@strawberry.type
class IncomeSchema:
    """
    Represents the schema for income information
    """

    description: str
    value: int
    area: str


@strawberry.type
class CrimeRateSchema:
    """
    Represents the schema for crime rate information
    """

    description: str
    value: float
    area: str


@strawberry.type
class SafetyRatingSchema:
    """
    Represents the schema for Safety Rating information
    """

    description: str
    value: float
    area: str


@strawberry.type
class Query:

    @strawberry.field
    def demographics(self, area: str) -> List[DemographicSchema]:
        """

        Args:
            area (str): The area for which traffic accidents data should be retrieved

        Returns:
            List[DemographicSchema]: A list of `DemographicSchema` objects

        """
        db = next(get_db())
        demographics = db.query(DemographicsModel).filter(
            DemographicsModel.area == area).all()

        return demographics



    @strawberry.field
    def unemployment_rate(self, area: str) -> List[EmploymentSchema]:
        """

        Args:
            area (str): The area for which traffic accidents data should be retrieved

        Returns:
            List[EmploymentSchema]: A list of `EmploymentSchema` objects

        """
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
        """

        Args:
            area (str): The area for which traffic accidents data should be retrieved

        Returns:
            List[TrafficAccidentsSchema]: A list of `TrafficAccidentsSchema` objects

        """
        db = next(get_db())
        data = db.query(TrafficAccidents).filter(
            TrafficAccidents.area == area).all()

        return data



    @strawberry.field
    def traffic_accidents_sum(self, area: str) -> List[TrafficAccidentsSchema]:
        """

        Args:
            area (str): The area for which traffic accidents data should be retrieved

        Returns:
            List[TrafficAccidentsSchema]: A list of `TrafficAccidentsSchema` objects (sum by years)

        """
        db = next(get_db())
        traffic_accidents = (db.query(
            TrafficAccidents.area, TrafficAccidents.year,
            func.sum(TrafficAccidents.value)).filter(
                TrafficAccidents.area == area).group_by(TrafficAccidents.year))

        result = []
        for a, year, total in traffic_accidents:
            result.append(
                TrafficAccidentsSchema(
                    description="Total traffic accidents per year",
                    area=a,
                    year=year,
                    value=total))

        return result



    @strawberry.field
    def education(self, area: str) -> List[EducationSchema]:
        """

        Args:
            area (str): The area for which traffic accidents data should be retrieved

        Returns:
            List[EducationSchema]: A list of `EducationSchema` objects

        """
        db = next(get_db())
        data = db.query(Education).filter(Education.area == area).all()

        return data

    @strawberry.field
    def income(self, area: str) -> List[IncomeSchema]:
        """

        Args:
            area: The area for which income data should be retrieved

        Returns:
            List[IncomeSchema]: A list of `IncomeSchema` objects

        """

        db = next(get_db())
        data = db.query(Income).filter(Income.area == area).all()

        return data


schema = strawberry.Schema(query=Query)
