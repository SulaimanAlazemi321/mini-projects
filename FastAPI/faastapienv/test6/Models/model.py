from sqlalchemy import Column, String, Integer, ForeignKey, Float, Text
from Models.database import base

class ecoUser(base):
    __tablename__ = "ecoUser"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    userType = Column(Integer, ForeignKey("ecoUsertypes.id"))


class ecoUsertypes(base):
    __tablename__ = "ecoUsertypes"
    
    id = Column(Integer, primary_key=True, index=True)
    usertype = Column(Integer, nullable=False)
    name = Column(String(50), nullable=False)


class ecoCategories(base):
    __tablename__ = "ecoCategories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)


class ecoFacilities(base):
    __tablename__ = "ecoFacilities"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(50), nullable=False)
    category = Column(Integer, ForeignKey("ecoCategories.id"))
    description = Column(String(150))
    houseNumber = Column(String(50))
    streetName = Column(String(50))
    county = Column(String(50))
    town = Column(String(50))
    postcode = Column(String(7))
    lng = Column(Float)
    lat = Column(Float)
    contributor = Column(Integer, ForeignKey("ecoUser.id"))


class ecoFacilityStatus(base):
    __tablename__ = "ecoFacilityStatus"
    
    id = Column(Integer, primary_key=True, index=True)
    facilityId = Column(Integer, ForeignKey("ecoFacilities.id"))
    statusComment = Column(String(100))
    contributor = Column(Integer, ForeignKey("ecoUser.id"))