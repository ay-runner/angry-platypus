from sqlalchemy import Column, DateTime
from sqlalchemy.orm import DeclarativeBase, declared_attr
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

# Base class declaration used by all models
class Base(DeclarativeBase):
    pass

class TimeStampMixin:
    '''
    Mixin adds date and time information to all entities for both their created_on and updated_on attributes
    '''

    @declared_attr
    def created_on(cls):
        return Column(
        DateTime(timezone=True),
        server_default = func.now(),
        nullable=False
    )
    
    @declared_attr
    def updated_on(cls):
        return Column(
        DateTime(timezone=True),
        server_default = func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
class BaseModel(Base, TimeStampMixin):
    '''
    Abstract Base Model
    All concret models inherit from this
    '''
    __abstract__ = True

    id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4,
        nullable=False
    )

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"