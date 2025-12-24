# Record models for HR Exchange
# This file contains various record and data models like IndividualData, MonthRecord, etc.

from pydantic import BaseModel, ConfigDict, Field
from typing import Annotated, Optional
from datetime import datetime
import pandas as pd
import pandera as pa
from pandera.typing import Series, DataFrame
from brynq_sdk_functions import BrynQPanderaDataFrameModel


class IndividualDataGet(BrynQPanderaDataFrameModel):
    """Schema for Individual Data rows, validated as separate DF; supports join via employee_id."""

    employee_id: Optional[Series[str]] = pa.Field(nullable=True)

    id: Optional[Series[str]] = pa.Field(nullable=True)
    long_field_name: Optional[Series[str]] = pa.Field(nullable=True)
    short_field_name: Optional[Series[str]] = pa.Field(nullable=True)
    date: Optional[Series[datetime]] = pa.Field(nullable=True)
    amount: Optional[Series[float]] = pa.Field(nullable=True)
    long_field_name2: Optional[Series[str]] = pa.Field(nullable=True)
    short_field_name2: Optional[Series[str]] = pa.Field(nullable=True)
    date2: Optional[Series[datetime]] = pa.Field(nullable=True)
    amount2: Optional[Series[float]] = pa.Field(nullable=True)
    long_field_name3: Optional[Series[str]] = pa.Field(nullable=True)
    short_field_name3: Optional[Series[str]] = pa.Field(nullable=True)
    date3: Optional[Series[datetime]] = pa.Field(nullable=True)
    amount3: Optional[Series[float]] = pa.Field(nullable=True)
    long_field_name4: Optional[Series[str]] = pa.Field(nullable=True)
    short_field_name4: Optional[Series[str]] = pa.Field(nullable=True)
    date4: Optional[Series[datetime]] = pa.Field(nullable=True)
    amount4: Optional[Series[float]] = pa.Field(nullable=True)
    long_field_name5: Optional[Series[str]] = pa.Field(nullable=True)
    short_field_name5: Optional[Series[str]] = pa.Field(nullable=True)
    date5: Optional[Series[datetime]] = pa.Field(nullable=True)
    amount5: Optional[Series[float]] = pa.Field(nullable=True)
    long_field_name6: Optional[Series[str]] = pa.Field(nullable=True)
    short_field_name6: Optional[Series[str]] = pa.Field(nullable=True)
    date6: Optional[Series[datetime]] = pa.Field(nullable=True)
    amount6: Optional[Series[float]] = pa.Field(nullable=True)
    long_field_name7: Optional[Series[str]] = pa.Field(nullable=True)
    short_field_name7: Optional[Series[str]] = pa.Field(nullable=True)
    date7: Optional[Series[datetime]] = pa.Field(nullable=True)
    amount7: Optional[Series[float]] = pa.Field(nullable=True)
    long_field_name8: Optional[Series[str]] = pa.Field(nullable=True)
    short_field_name8: Optional[Series[str]] = pa.Field(nullable=True)
    date8: Optional[Series[datetime]] = pa.Field(nullable=True)
    amount8: Optional[Series[float]] = pa.Field(nullable=True)

    class Config:
        coerce = True

    class _Annotation:
        primary_keys = ["employee_id", "id"]
