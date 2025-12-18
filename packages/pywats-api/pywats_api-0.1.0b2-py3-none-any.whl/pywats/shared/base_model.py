"""Base model for all pyWATS models.

Provides consistent Pydantic 2 configuration for serialization/deserialization.
"""
from pydantic import BaseModel, ConfigDict


class PyWATSModel(BaseModel):
    """
    Base class for all pyWATS models.

    Provides consistent Pydantic 2 configuration for serialization/deserialization.
    """
    model_config = ConfigDict(
        populate_by_name=True,          # Allow using field names or aliases
        use_enum_values=True,           # Serialize enums as values
        arbitrary_types_allowed=True,   # Allow custom types
        from_attributes=True,           # Allow creating from ORM objects
        validate_assignment=True,       # Validate on attribute assignment
    )
