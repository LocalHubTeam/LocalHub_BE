from sqlalchemy import Column, Integer, String, Text, Float, DateTime
from datetime import datetime
from .database import Base

class LocationType(Base):
    __tablename__ = "location_types"
    contenttypeid = Column(String, primary_key=True)
    name = Column(String, nullable=False)

class Location(Base):
    __tablename__ = "locations"
    contentid = Column(String, primary_key=True)
    contenttypeid = Column(String, index=True, nullable=False)
    title = Column(String, nullable=False)
    addr1 = Column(String)
    addr2 = Column(String)
    tel = Column(String)
    mapx = Column(Float)
    mapy = Column(Float)
    lDongRegnCd = Column(String, index=True)
    lDongSignguCd = Column(String, index=True)
    lclsSystm1 = Column(String)
    lclsSystm2 = Column(String, index=True)
    lclsSystm3 = Column(String)
    firstimage = Column(String)
    firstimage2 = Column(String)
    createdtime = Column(String)
    modifiedtime = Column(String)

class DataSource(Base):
    __tablename__ = "data_sources"
    id = Column(Integer, primary_key=True, autoincrement=True)
    contenttypeid = Column(String, index=True)
    filename = Column(String, nullable=False)
    source_org = Column(String)
    license_type = Column(String)
    collected_count = Column(Integer)

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String, nullable=False, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    password = Column(String, nullable=False)
    view_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)