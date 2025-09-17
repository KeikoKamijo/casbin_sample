from sqlalchemy import Column, Integer, ForeignKey, Table
from . import Base

# Association table for many-to-many relationship between Corporation and Shop
corporation_shop = Table(
    'corporation_shop',
    Base.metadata,
    Column('corporation_id', Integer, ForeignKey('corporations.id'), primary_key=True),
    Column('shop_id', Integer, ForeignKey('shops.id'), primary_key=True)
)