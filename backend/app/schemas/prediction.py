from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator
)


class PredictionFeatures(BaseModel):

    model_config = ConfigDict(extra="forbid")

    age: int = Field(ge=18, le=85)

    daily_doses: int = Field(ge=1, le=4)

    missed_doses_7d: int = Field(ge=0, le=28)

    adherence_rate_30d: float = Field(
        ge=0,
        le=1
    )

    reminder_response_rate: float = Field(
        ge=0,
        le=1
    )

    medication_count: int = Field(
        ge=1,
        le=6
    )

    chronic_condition_count: int = Field(
        ge=1,
        le=3
    )

    previous_non_adherence: Literal[0, 1]

    @model_validator(mode="after")
    def validate_missed_doses(self):

        maximum_doses = self.daily_doses * 7

        if self.missed_doses_7d > maximum_doses:

            raise ValueError(
                "Missed doses cannot exceed "
                "total scheduled weekly doses"
            )

        return self


class PredictionResult(BaseModel):

    risk_score: float = Field(
        ge=0,
        le=100
    )

    risk_level: Literal[
        "Low",
        "Medium",
        "High"
    ]

    model_version: str

    model_sha256: str

    algorithm: str

    dataset_type: str

    disclaimer: str

class PredictionCreate(BaseModel):

    model_config = ConfigDict(extra="forbid")

    patient_id: int = Field(gt=0)

    features: PredictionFeatures