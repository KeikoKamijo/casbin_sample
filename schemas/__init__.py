from .users import User, UserBase, UserCreate, UserUpdate
from .corporations import Corporation, CorporationBase, CorporationCreate, CorporationUpdate, CorporationWithUsers, CorporationWithSchools
from .schools import School, SchoolBase, SchoolCreate, SchoolUpdate, SchoolWithCorporations
from .inquiries import Inquiry, InquiryBase, InquiryCreate, InquiryUpdate, InquiryAssign, InquiryStatusUpdate, InquiryWithDetails

__all__ = [
    # Users
    "User", "UserBase", "UserCreate", "UserUpdate",
    # Corporations
    "Corporation", "CorporationBase", "CorporationCreate", "CorporationUpdate",
    "CorporationWithUsers", "CorporationWithSchools",
    # Schools
    "School", "SchoolBase", "SchoolCreate", "SchoolUpdate", "SchoolWithCorporations",
    # Inquiries
    "Inquiry", "InquiryBase", "InquiryCreate", "InquiryUpdate", "InquiryAssign",
    "InquiryStatusUpdate", "InquiryWithDetails"
]