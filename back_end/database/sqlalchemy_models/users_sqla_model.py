from sqlalchemy import Column, String, Boolean, Enum as SQLEnum, ForeignKey, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.orm.attributes import flag_modified
import enum
from .base_sqla_model import BaseModel

class UserRole(enum.Enum):
    """
    Enum for user roles in the system.
    Note: Users can have multiple roles across different assessments,
    but this represents their primary system role.
    """
    ADMIN = "admin"
    USER = "user"


class UserTypeDefinition(BaseModel):
    """
    Defines custom user type schemas for organizations.
    Allows app users to create their own user types with custom fields.
    
    Example:
        Navy Personnel type with fields: ship_assignment, deployment_date
        Sales Team type with fields: territory, quota, commission_rate
    """
    __tablename__ = "user_type_definitions"
    
    # Type identification
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # JSON schema defining the custom fields and their validation rules
    field_schema = Column(JSONB, nullable=False, default=dict)
    
    # Example structure:
    # {
    #     "ship_assignment": {
    #         "type": "string",
    #         "label": "Ship Assignment",
    #         "required": true,
    #         "max_length": 100
    #     },
    #     "deployment_date": {
    #         "type": "date",
    #         "label": "Deployment Date",
    #         "required": false
    #     },
    #     "security_clearance": {
    #         "type": "select",
    #         "label": "Security Clearance",
    #         "options": ["Confidential", "Secret", "Top Secret"],
    #         "required": true
    #     }
    # }
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    users = relationship("User", back_populates="custom_type_definition")
    
    def __repr__(self):
        return f"<UserTypeDefinition(id={self.id}, name='{self.name}')>"
    
class User(BaseModel):
    """
    Base user model - applies to all app users, evaluators, and testers.
    Uses joined table inheritance for predefined extensions (MilitaryUser, etc.)
    and JSONB for custom fields defined by app users.
    
    A user can participate in assessments as:
    - An evaluator/proctor (assessing others)
    - A tester/student/employee (being assessed)
    - Both roles in different assessments
    """
    __tablename__ = "users"
    
    # Core user attributes
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    
    # System role (for app permissions via Authentik)
    role = Column(
    SQLEnum(UserRole, values_callable=lambda x: [e.value for e in x]),
    nullable=False,
    default=UserRole.USER
    )
    
    # Account status
    is_active = Column(Boolean, default=True, nullable=False)

    # Discriminator for polymorphic inheritance (predefined types)
    user_type = Column(String(50))
    
    # Link to custom type definition (for user-defined types)
    custom_type_definition_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("user_type_definitions.id"), 
        nullable=True,
        index=True
    )
    
    # Store custom field values (validated against custom_type_definition.field_schema)
    custom_fields = Column(JSONB, nullable=True, default=dict)

    # Example:
    # {
    #     "ship_assignment": "USS Enterprise",
    #     "deployment_date": "2025-06-15",
    #     "security_clearance": "Top Secret"
    # }
    
    # Relationships
    custom_type_definition = relationship("UserTypeDefinition", back_populates="users")
    
    assessments_as_tester = relationship(
        "Assessment", 
        foreign_keys="Assessment.tester_id", 
        back_populates="tester"
    )
    assessments_as_evaluator = relationship(
        "Assessment", 
        foreign_keys="Assessment.evaluator_id", 
        back_populates="evaluator"
    )
    
    # Polymorphic configuration
    __mapper_args__ = {
        "polymorphic_on": user_type,
        "polymorphic_identity": "user"
    }
    
    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', email='{self.email}')>"
    
    @property
    def is_admin(self):
        """Convenience property to check admin status"""
        return self.role == UserRole.ADMIN
    
    def get_custom_field(self, field_name: str, default=None):
        """Safely retrieve a custom field value"""
        if self.custom_fields is not None:
            return self.custom_fields.get(field_name, default)
        return default

def set_custom_field(self, field_name: str, value):
    """Set a custom field value"""
    if self.custom_fields is None:
        self.custom_fields = {}
    fields = dict(self.custom_fields)  # Create a new dict
    fields[field_name] = value
    self.custom_fields = fields
    flag_modified(self, 'custom_fields')


class MilitaryBranch(enum.Enum):
    """Enum for military branches"""
    ARMY = "army"
    NAVY = "navy"
    AIR_FORCE = "air_force"
    MARINES = "marines"
    SPACE_FORCE = "space_force"
    COAST_GUARD = "coast_guard"


class MilitaryUser(User):
    """
    Military-specific user extension.
    Provides predefined common military fields.
    Can still use custom_fields for additional organization-specific data.
    
    Example: A Navy organization might use predefined fields (rank, branch)
    plus custom_fields for {"ship_assignment": "USS Enterprise"}
    """
    __tablename__ = "military_users"
    
    id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    
    # Predefined military fields (common across all military users)
    rank = Column(String(50), nullable=True)
    unit = Column(String(255), nullable=True)
    mos = Column(String(50), nullable=True)  # Military Occupational Specialty
    branch = Column(SQLEnum(MilitaryBranch), nullable=True)
    service_number = Column(String(50), nullable=True, index=True)
    clearance_level = Column(String(50), nullable=True)
    
    __mapper_args__ = {
        "polymorphic_identity": "military_user"
    }
    
    def __repr__(self):
        branch = self.branch
        branch_str = f", {branch.value}" if branch is not None else ""
        return f"<MilitaryUser(id={self.id}, rank='{self.rank}', name='{self.name}'{branch_str})>"
    
    @property
    def full_title(self):
        """Returns formatted military title with rank and name"""
        rank = self.rank
        if rank is not None:
            return f"{rank} {self.name}"
        return self.name


# Future predefined user type extensions can be added here:
# 
# class CorporateUser(User):
#     """Corporate/HR-specific user extension with predefined fields"""
#     __tablename__ = "corporate_users"
#     
#     id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
#     
#     employee_id = Column(String(50), nullable=True, index=True)
#     department = Column(String(255), nullable=True)
#     position = Column(String(255), nullable=True)
#     hire_date = Column(Date, nullable=True)
#     
#     __mapper_args__ = {
#         "polymorphic_identity": "corporate_user"
#     }
#     
#     # Can still use custom_fields for organization-specific data
#     # Example: {"cost_center": "ENG-001", "manager_email": "boss@company.com"}
# 
# class MedicalUser(User):
#     """Medical/healthcare-specific user extension with predefined fields"""
#     __tablename__ = "medical_users"
#     
#     id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
#     
#     license_number = Column(String(50), nullable=True, index=True)
#     specialty = Column(String(255), nullable=True)
#     certification_level = Column(String(50), nullable=True)
#     
#     __mapper_args__ = {
#         "polymorphic_identity": "medical_user"
#     }
#     
#     # Can still use custom_fields for organization-specific data
#     # Example: {"hospital_affiliation": "General Hospital", "pager": "555-1234"}
