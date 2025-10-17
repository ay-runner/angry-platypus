"""
Models package - contains all SQLAlchemy ORM definitions.

Import all models here so they can be accessed via:
    from models import User, MilitaryUser, Scenario, etc.
"""

from .base_sqla_model import Base, BaseModel, TimeStampMixin
from .users_sqla_model import User, MilitaryUser, UserRole
# from .scenarios import Scenario
# from .engagements import Engagement
# from .assessments import Assessment

# This list defines what gets imported with "from models import *"
__all__ = [
    # Base classes
    "Base",
    "BaseModel",
    "TimeStampMixin",
    
    # User models
    "User",
    "MilitaryUser",
    "UserRole",
    
    # # Scenario models
    # "Scenario",
    
    # # Engagement models
    # "Engagement",
    
    # # Evaluation models
    # "Assessment"
]