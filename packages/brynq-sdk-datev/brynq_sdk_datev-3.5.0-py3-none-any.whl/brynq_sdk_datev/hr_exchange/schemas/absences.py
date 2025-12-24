# Absence models for HR Exchange
# This file contains absence-related models for different payroll systems

from pydantic import BaseModel, ConfigDict, Field
from typing import Annotated, Optional
from datetime import datetime
import pandas as pd
import pandera as pa
from pandera.typing import Series, DataFrame
from brynq_sdk_functions import BrynQPanderaDataFrameModel
from ._enums import ReasonForAbsence, ReasonForAbsence1


class AbsenceLug(BaseModel):
    """Absence model for Lohn und Gehalt (LuG) payroll system"""
    model_config = ConfigDict(
        extra='allow',
    )
    id: Annotated[str | None, Field(ge=1, le=2147483647)] = None
    personnel_number: Annotated[int | None, Field(examples=[12345], ge=1, le=99999)] = (
        None
    )
    date_of_emergence: Annotated[
        datetime | None, Field(examples=['2021-01-01'], max_length=10)
    ] = None
    reason_for_absence: Annotated[ReasonForAbsence | None, Field(examples=['K'])] = None
    """
    For an explanation of codes, see <a href='https://apps.datev.de/help-center/documents/9222265'>Tabelle der Ausfallschlüssel - DATEV Hilfe-Center</a>
    """


class AbsenceLodas(BaseModel):
    """Absence model for LODAS payroll system"""
    model_config = ConfigDict(
        extra='allow',
    )
    personnel_number: Annotated[int | None, Field(examples=[12345], ge=1, le=99999)] = (
        None
    )
    absence_start_date: Annotated[
        datetime | None, Field(examples=['2021-01-01'], max_length=10)
    ] = None
    absence_end_date: Annotated[
        datetime | None, Field(examples=['2021-01-01'], max_length=10)
    ] = None
    reason_for_absence: Annotated[ReasonForAbsence1 | None, Field(examples=[32])] = None


class AbsenceLugGet(BrynQPanderaDataFrameModel):
    """Flattened schema for LuG absences (GET)."""

    id: Optional[Series[str]] = pa.Field(nullable=True)
    personnel_number: Series[pd.Int64Dtype] = pa.Field(nullable=True)
    date_of_emergence: Optional[Series[datetime]] = pa.Field(nullable=True)
    # reason_for_absence is a coded string for LuG; we accept as free text here
    reason_for_absence: Optional[Series[str]] = pa.Field(nullable=True)

    class Config:
        coerce = True

    class _Annotation:
        primary_keys = ["id", "personnel_number"]


class AbsenceLodasGet(BrynQPanderaDataFrameModel):
    """Flattened schema for LODAS absences (GET)."""

    personnel_number: Series[pd.Int64Dtype] = pa.Field(nullable=True)
    absence_start_date: Optional[Series[datetime]] = pa.Field(nullable=True)
    absence_end_date: Optional[Series[datetime]] = pa.Field(nullable=True)
    reason_for_absence: Series[pd.Int64Dtype] = pa.Field(nullable=True, isin=[m.value for m in ReasonForAbsence1])

    class Config:
        coerce = True

    class _Annotation:
        primary_keys = ["personnel_number", "absence_start_date"]
