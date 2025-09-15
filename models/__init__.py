from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Import all models to ensure they are registered with SQLAlchemy
from .associations import corporation_school
from .users import User
from .corporations import Corporation
from .schools import School
from .inquiries import Inquiry

__all__ = [
    "Base",
    "corporation_school",
    "User",
    "Corporation",
    "School",
    "Inquiry"
]