from pydantic import BaseModel, Field, ConfigDict, UUID7, Json
from database.sqlalchemy_models.users_sqla_model import UserRole, MilitaryBranch
from datetime import datetime

class UserSchema(BaseModel):
    name: str
    email: str
    role: UserRole
    is_active: bool
    user_type: str
    custom_type_definition_id: UUID7
    custom_fields: Json
    id: UUID7
    created_on: datetime
    updated_on: datetime

class MilitaryUserSchema(UserSchema):
    id: UUID7
    rank: str
    unit: str
    mos: str
    branch: MilitaryBranch
    service_number: str
    clearance_level: str
    