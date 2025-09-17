from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Import all models to ensure they are registered with SQLAlchemy
from .associations import corporation_shop
from .users import User
from .corporations import Corporation
from .shops import Shop
from .inquiries import Inquiry
from .roles import Role

__all__ = [
    "Base",
    "corporation_shop",
    "User",
    "Corporation",
    "Shop",
    "Inquiry",
    "Role"
]