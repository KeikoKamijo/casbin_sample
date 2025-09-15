from sqlalchemy import Column, Integer, ForeignKey, Table
from . import Base

# Association table for many-to-many relationship between Corporation and School
corporation_school = Table(
    'corporation_school',
    Base.metadata,
    Column('corporation_id', Integer, ForeignKey('corporations.id'), primary_key=True),
    Column('school_id', Integer, ForeignKey('schools.id'), primary_key=True)
)