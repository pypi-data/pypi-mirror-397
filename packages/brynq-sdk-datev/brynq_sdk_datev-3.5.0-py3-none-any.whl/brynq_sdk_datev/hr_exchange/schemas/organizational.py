# Organizational models for HR Exchange
# This file contains organizational structure models like Client, Address, BusinessUnit, etc.

from pydantic import BaseModel, ConfigDict, Field
from typing import Annotated, List, Optional
from datetime import datetime
from ._enums import Country
import pandas as pd
import pandera as pa
from pandera.typing import Series, DataFrame
from brynq_sdk_functions import BrynQPanderaDataFrameModel

class ClientGet(BrynQPanderaDataFrameModel):
    """Schema for core client data without nested lists"""

    # Core Client fields only
    name: Optional[Series[str]] = pa.Field(nullable=True)
    is_test_client: Optional[Series[bool]] = pa.Field(nullable=True)
    instant_registration_required: Optional[Series[bool]] = pa.Field(nullable=True)
    current_accounting_month: Optional[Series[datetime]] = pa.Field(nullable=True)

    # Program fields (flattened)
    product: Optional[Series[str]] = pa.Field(alias="program.product", nullable=True)
    variant: Series[pd.Int64Dtype] = pa.Field(alias="program.variant", nullable=True)
    version: Optional[Series[str]] = pa.Field(alias="program.version", nullable=True)

    class Config:
        coerce = True

    class _Annotation:
        primary_keys = ["name"]


class SalaryTypeGet(BrynQPanderaDataFrameModel):
    """Schema for salary types data"""

    id: Series[pd.Int64Dtype] = pa.Field(nullable=True)
    name: Optional[Series[str]] = pa.Field(nullable=True)
    client_name: Optional[Series[str]] = pa.Field(nullable=True)  # Added for relationship tracking

    class Config:
        coerce = True

    class _Annotation:
        primary_keys = ["id", "client_name"]


class DepartmentGet(BrynQPanderaDataFrameModel):
    """Schema for departments data"""

    id: Optional[Series[str]] = pa.Field(nullable=True)
    name: Optional[Series[str]] = pa.Field(nullable=True)
    contact_person: Optional[Series[str]] = pa.Field(nullable=True)
    client_name: Optional[Series[str]] = pa.Field(nullable=True)  # Added for relationship tracking

    class Config:
        coerce = True

    class _Annotation:
        primary_keys = ["id", "client_name"]


class CostCenterGet(BrynQPanderaDataFrameModel):
    """Schema for cost centers data"""

    id: Optional[Series[str]] = pa.Field(nullable=True)
    name: Optional[Series[str]] = pa.Field(nullable=True)
    client_name: Optional[Series[str]] = pa.Field(nullable=True)  # Added for relationship tracking

    class Config:
        coerce = True

    class _Annotation:
        primary_keys = ["id", "client_name"]


class HealthInsurerGet(BrynQPanderaDataFrameModel):
    """Schema for health insurers data"""

    id: Optional[Series[str]] = pa.Field(nullable=True)
    name: Optional[Series[str]] = pa.Field(nullable=True)
    company_number_of_health_insurer: Optional[Series[str]] = pa.Field(nullable=True)
    client_name: Optional[Series[str]] = pa.Field(nullable=True)  # Added for relationship tracking

    class Config:
        coerce = True

    class _Annotation:
        primary_keys = ["id", "client_name"]


class BusinessUnitGet(BrynQPanderaDataFrameModel):
    """Schema for business units data"""

    id: Optional[Series[str]] = pa.Field(nullable=True)
    name: Optional[Series[str]] = pa.Field(nullable=True)
    client_name: Optional[Series[str]] = pa.Field(nullable=True)  # Added for relationship tracking

    class Config:
        coerce = True

    class _Annotation:
        primary_keys = ["id", "client_name"]
