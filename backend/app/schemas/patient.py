from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field
)


class PatientCreate(BaseModel):

    model_config = ConfigDict(
        str_strip_whitespace=True
    )

    name: str = Field(
        min_length=2,
        max_length=150
    )

    age: int = Field(
        ge=1,
        le=120
    )

    condition: str = Field(
        min_length=2,
        max_length=100
    )


class PatientResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    name: str
    age: int
    condition: str
    created_at: datetime