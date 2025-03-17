import os
from sqlalchemy import Column, Integer, String, Float, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DB_path = os.path.join(os.path.dirname(__file__), '..', 'db', 'combined_db.sqlite3')
DB_URL = f"sqlite:///{DB_path}"

engine = create_engine(DB_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()



# Demographics
class DemographicsModel(Base):
    __tablename__ = "demographics"

    id = Column(Integer, primary_key=True, index=True)
    area = Column(String, index=True)
    description = Column(String)
    value = Column(Float)


# Traffic accidents
class TrafficAccidents(Base):
    __tablename__ = "traffic_accidents"

    id = Column(Integer, primary_key=True, index=True)
    area = Column(String, index=True)
    year = Column(Integer)
    description = Column(String)
    value = Column(Integer)


class EmploymentRate(Base):
    __tablename__ = "employment_rate"

    id = Column(Integer, primary_key=True, index=True)
    area = Column(String, index=True)
    timeframe = Column(String)
    description = Column(String)
    value = Column(Float)


class CrimeRate(Base):
    __tablename__ = "crime_rate"

    id = Column(Integer, primary_key=True, index=True)
    area = Column(String, index=True)
    timeframe = Column(String)
    description = Column(String)
    value = Column(Integer)


class Income(Base):
    __tablename__ = "income"

    id = Column(Integer, primary_key=True, index=True)
    area = Column(String, index=True)
    description = Column(String)
    value = Column(Integer)

class Education(Base):
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