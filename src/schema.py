# pylint: disable=R0903

from statistics import mean
from typing import List

import strawberry
import numpy as np
from sqlalchemy.sql import func

from models import DemographicsModel, EmploymentRate, TrafficAccidents, Education, CrimeRate, Income, get_db


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
    timeframe: str
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
            TrafficAccidents.area, TrafficAccidents.timeframe,
            func.sum(TrafficAccidents.value)).filter(
                TrafficAccidents.area == area).group_by(TrafficAccidents.timeframe))

        result = []
        for a, timeframe, total in traffic_accidents:
            result.append(
                TrafficAccidentsSchema(
                    description="Total traffic accidents per year",
                    area=a,
                    timeframe=timeframe,
                    value=total))

        return result

    @strawberry.field
    def education(self, area: str) -> List[EducationSchema]:
        """

        Args:
            area (str): The area for which education data should be retrieved

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

    @strawberry.field
    def crimes(self, area: str) -> List[CrimeRateSchema]:

        db = next(get_db())
        q = (db.query(
            CrimeRate.area, CrimeRate.description,
            func.sum(CrimeRate.value)).filter(CrimeRate.area == area).group_by(
                CrimeRate.description))

        result = []
        for a, b, c in q:
            result.append(CrimeRateSchema(area=a, description=b, value=c))

        return result

    @strawberry.field
    def safety_rating(self, area: str) -> SafetyRatingSchema:

        total_weighted_crime = 0
        crime_weights = {
            "Total of thefts 28:1-3": 1.0,
            "Robbery 31:1-2 total": 2.5,
            "Damage to property 35:1-3 total": 1.2,
            "Offences against life total 21:1-3,34a:1": 5.0,
            "Sexual crimes": 4.5,
            "Crimes against public authority and public peace": 3.0,
            "Endangerment of traffic safety, hit-and-run 23:1,11": 2.0,
            "Aggravated endangerment of traffic safety 23:2": 2.8,
            "Drunken driving 23:3-4 total": 1.5,
            "Offences involving narcotics 50:1-4": 2.3
        }

        db = next(get_db())

        population_data = (db.query(DemographicsModel).filter(
            DemographicsModel.area == area,
            DemographicsModel.description == 'Population 31 Dec').first())

        crime_data = (db.query(
            CrimeRate.area, CrimeRate.description,
            func.sum(CrimeRate.value).label('total_crimes')).filter(
                CrimeRate.area == area).group_by(CrimeRate.description))

        for crime_record in crime_data:
            crime_description = crime_record.description
            crime_total = crime_record.total_crimes

            matched_weight = None

            for crime_type, weight in crime_weights.items():

                if crime_type in crime_description:
                    matched_weight = weight
                    break

            if matched_weight is not None:
                total_weighted_crime += crime_total * matched_weight

        crime_rate_per_100k = (total_weighted_crime /
                               population_data.value) * 100_000
        safety_rating = round(np.clip(200 * np.exp(-0.0002 * crime_rate_per_100k), 0,
                                99.5), 2)

        return SafetyRatingSchema(
            area=area,
            description="Safety Rating",
            value=safety_rating,
        )


schema = strawberry.Schema(query=Query)
