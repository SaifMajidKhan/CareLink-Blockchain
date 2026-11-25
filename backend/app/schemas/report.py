from pydantic import BaseModel, ConfigDict, Field


class ReportCreate(BaseModel):

    model_config = ConfigDict(extra="forbid")

    prediction_id: int = Field(gt=0)