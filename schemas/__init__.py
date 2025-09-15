from .users import User, UserBase, UserCreate, UserUpdate
from .corporations import Corporation, CorporationBase, CorporationCreate, CorporationUpdate
from .schools import School, SchoolBase, SchoolCreate, SchoolUpdate
from .inquiries import Inquiry, InquiryBase, InquiryCreate, InquiryUpdate, InquiryAssign, InquiryStatusUpdate
from .auth import LoginRequest, Token, TokenData

__all__ = [
    # Users
    "User", "UserBase", "UserCreate", "UserUpdate",
    # Corporations
    "Corporation", "CorporationBase", "CorporationCreate", "CorporationUpdate",
    # Schools
    "School", "SchoolBase", "SchoolCreate", "SchoolUpdate",
    # Inquiries
    "Inquiry", "InquiryBase", "InquiryCreate", "InquiryUpdate", "InquiryAssign",
    "InquiryStatusUpdate",
    # Auth
    "LoginRequest", "Token", "TokenData"
]