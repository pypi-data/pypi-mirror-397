# Financial models for HR Exchange
# This file contains financial-related models like Account, GrossPayment, HourlyWage, etc.

from pydantic import BaseModel, ConfigDict, Field
from typing import Annotated, Optional
from ._enums import PaymentMethod
import pandas as pd
import pandera as pa
from pandera.typing import Series, DataFrame
from brynq_sdk_functions import BrynQPanderaDataFrameModel


class Account(BaseModel):
    model_config = ConfigDict(
        extra='allow',
    )
    iban: Annotated[
        str | None,
        Field(
            max_length=34,
            pattern='^((AD|FI|AT|BE|BG|HR|CY|CZ|DK|EE|FI|FR|GF|DE|GI|GR|GP|HU|IS|IE|IT|LV|LI|LT|LU|MT|MQ|YT|MC|NL|NO|PL|PT|RE|RO|BL|MF|PM|SM|SK|SI|ES|SE|CH|GB|VA)\\d\\d([A-Za-z0-9]){11,30})$',
        ),
    ] = None
    bic: Annotated[
        str | None,
        Field(
            max_length=11,
            pattern='^([A-Z]{4}(FI|AT|BE|BG|HR|CY|CZ|DK|EE|FI|FR|GF|DE|GI|GR|GP|HU|IS|IE|IT|LV|LI|LT|LU|MT|MQ|YT|MC|NL|NO|PL|PT|RE|RO|BL|MF|PM|SM|SK|SI|ES|SE|CH|GB)([A-Z0-9]){2}([A-Z0-9]){0,3})$',
        ),
    ] = None
    differing_account_holder: Annotated[
        str | None, Field(max_length=25, pattern='^[a-zA-Z0-9_]*$')
    ] = None


class GrossPaymentCreate(BaseModel):
    model_config = ConfigDict(
        extra='allow',
    )
    id: Annotated[int | None, Field(ge=1, le=99)] = None
    amount: Annotated[float, Field(ge=-999999.99, le=999999.99)]
    salary_type_id: Annotated[int, Field(ge=1, le=9999)]
    payment_months: Annotated[str, Field(max_length=30)]


class GrossPayment(BaseModel):
    model_config = ConfigDict(
        extra='allow',
    )
    id: Annotated[int | None, Field(ge=1, le=99)] = None
    amount: Annotated[float, Field(ge=-999999.99, le=999999.99)]
    salary_type_id: Annotated[int, Field(ge=1, le=9999)]
    payment_months: Annotated[str, Field(max_length=30)]


class HourlyWage(BaseModel):
    model_config = ConfigDict(
        extra='allow',
    )
    id: Annotated[int | None, Field(ge=1, le=5)] = None
    amount: Annotated[float, Field(ge=0.0, le=99.99)]


class GrossPaymentGet(BrynQPanderaDataFrameModel):
    """Schema for list of gross payments per employee"""

    # Parent link
    employee_id: Optional[Series[str]] = pa.Field(nullable=True)

    # Fields from GrossPayment
    id: Optional[Series[pd.Int64Dtype]] = pa.Field(nullable=True)
    amount: Series[float] = pa.Field(nullable=True)
    salary_type_id: Series[pd.Int64Dtype] = pa.Field(nullable=True)
    payment_months: Optional[Series[str]] = pa.Field(nullable=True)

    class Config:
        coerce = True

    class _Annotation:
        primary_keys = ["employee_id", "id"]


class HourlyWageGet(BrynQPanderaDataFrameModel):
    """Schema for list of hourly wages per employee"""

    # Parent link
    employee_id: Optional[Series[str]] = pa.Field(nullable=True)

    # Fields from HourlyWage
    id: Optional[Series[pd.Int64Dtype]] = pa.Field(nullable=True)
    amount: Series[float] = pa.Field(nullable=True)

    class Config:
        coerce = True

    class _Annotation:
        primary_keys = ["employee_id", "id"]
