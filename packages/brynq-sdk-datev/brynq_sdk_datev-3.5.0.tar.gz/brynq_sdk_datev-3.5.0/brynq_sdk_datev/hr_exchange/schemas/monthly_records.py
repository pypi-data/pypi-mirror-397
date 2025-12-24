from pydantic import BaseModel, ConfigDict, Field
from typing import Annotated, Optional
import pandas as pd
import pandera as pa
from pandera.typing import Series, DataFrame
from brynq_sdk_functions import BrynQPanderaDataFrameModel


class MonthRecord(BaseModel):
    model_config = ConfigDict(
        extra='allow',
    )
    personnel_number: int | None = None
    value: float | None = None
    salary_type_id: int | None = None
    differing_factor: float | None = None
    cost_center_id: str | None = None
    month_of_emergence: str | None = None
    processing_code: int | None = None


class MonthRecordGet(BrynQPanderaDataFrameModel):
    """Schema for Month Records rows; validated as a separate DataFrame."""

    # Parent link for joins
    employee_id: Optional[Series[str]] = pa.Field(nullable=True)

    personnel_number: Series[pd.Int64Dtype] = pa.Field(nullable=True)
    value: Optional[Series[float]] = pa.Field(nullable=True)
    salary_type_id: Series[pd.Int64Dtype] = pa.Field(nullable=True)
    differing_factor: Optional[Series[float]] = pa.Field(nullable=True)
    cost_center_id: Optional[Series[str]] = pa.Field(nullable=True)
    month_of_emergence: Optional[Series[str]] = pa.Field(nullable=True)
    processing_code: Series[pd.Int64Dtype] = pa.Field(nullable=True)

    class Config:
        coerce = True
