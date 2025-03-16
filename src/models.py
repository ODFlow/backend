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
    accident_id = Column(Integer, primary_key=True, index=True)
    area = Column(String, index=True)
    year = Column(Integer)
    accident_type = Column(String)
    value = Column(Integer)

class EmploymentRate(Base):
    __tablename__ = "employment_rate"
    id = Column(Integer, primary_key=True)
    area = Column(String, primary_key=True)
    timeframe = Column(String)
    description = Column(String)
    value = Column(Float)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()