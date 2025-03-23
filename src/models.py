# pylint: disable=R0903


"""

Module for database models, defining the structure of tables

"""


import os
from sqlalchemy import Column, Integer, String, Float, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DB_path = os.path.join(os.path.dirname(__file__), '..', 'db',
                       'combined_db.sqlite3')
DB_URL = f"sqlite:///{DB_path}"

engine = create_engine(DB_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()



# Demographics
class DemographicsModel(Base):
    """
    Represents the demographics table in the database.

    Attributes:
        id (int): Primary key
        area (str): Area of the demographics data
        description (str): Type of the demographics data
        value (int): demographics data value
    """
    __tablename__ = "demographics"

    id = Column(Integer, primary_key=True, index=True)
    area = Column(String, index=True)
    description = Column(String)
    value = Column(Float)


# Traffic accidents
class TrafficAccidents(Base):
    """
    Represents the traffic_accidents table in the database.

    Attributes:
        id (int): Primary key
        area (str): Area of the traffic accidents data
        timeframe (str): Time period for the traffic accidents
        description (str): Type of the traffic accidents data
        value (int): Traffic accidents data value
    """
    __tablename__ = "traffic_accidents"

    id = Column(Integer, primary_key=True, index=True)
    area = Column(String, index=True)
    timeframe = Column(String)
    description = Column(String)
    value = Column(Integer)


class EmploymentRate(Base):
    """
    Represents the employment_rate table in the database.

    Attributes:
        id (int): Primary key
        area (str): Area of the crime rate data
        timeframe (str): Time period for the employment rate
        description (str): Type of the employment rate data
        value (int): Employment data value
    """
    __tablename__ = "employment_rate"

    id = Column(Integer, primary_key=True, index=True)
    area = Column(String, index=True)
    timeframe = Column(String)
    description = Column(String)
    value = Column(Float)


class CrimeRate(Base):
    """
    Represents the crime_rate table in the database.

    Attributes:
        id (int): Primary key
        area (str): Area of the crime rate data
        timeframe (str): Time period of the crime rate
        description (str): Type of the crime
        value (int): Crime data value
    """
    __tablename__ = "crime_rate"

    id = Column(Integer, primary_key=True, index=True)
    area = Column(String, index=True)
    timeframe = Column(String)
    description = Column(String)
    value = Column(Integer)


class Income(Base):
    """
    Represents the income table in the database.

    Attributes:
        id (int): Primary key
        area (str): Area of the income data
        description (str): Type of the income
        value (int): Income data value
    """

    __tablename__ = "income"

    id = Column(Integer, primary_key=True, index=True)
    area = Column(String, index=True)
    description = Column(String)
    value = Column(Integer)


class Education(Base):
    """
    Represents the education table in the database.

    Attributes:
        id (int): Primary key
        area (str): Area of the education data
        age (str): Age
        description (str): Type of the education data
        value (int): Education data value
    """
    __tablename__ = "education"

    id = Column(Integer, primary_key=True, index=True)
    area = Column(String, index=True)
    age = Column(String)
    description = Column(String)
    value = Column(Integer)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
