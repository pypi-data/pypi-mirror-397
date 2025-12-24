from datetime import datetime
import pandera as pa
from pandera.typing import Series, DataFrame
from typing import Optional, List, Union, Annotated
from uuid import UUID
from brynq_sdk_functions import BrynQPanderaDataFrameModel
import pandas as pd
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from ._enums import (
    Sex, PaymentMethod, Country, ContributionClassHealthInsurance,
    ContributionClassPensionInsurance, EmployeeType, ContractualStructure,
    HighestLevelOfProfessionalTraining, HighestLevelOfEducation,
    Denomination, SpousesDenomination, EmploymentType, FlatRateTax
    # NamePrefix, NameAffix, BirthNamePrefix, BirthNameAffix
)



class EmployeeGet(BrynQPanderaDataFrameModel):
    """Flattened schema for employee data that combines all nested objects into a single flat structure"""

    # Core Employee fields
    id: Optional[Series[str]] = pa.Field(alias="employee_id", nullable=True)
    surname: Series[str] = pa.Field()
    client_id: Optional[Series[str]] = pa.Field(nullable=True)
    personnel_number: Series[pd.Int64Dtype] = pa.Field(nullable=True)
    company_personnel_number: Optional[Series[str]] = pa.Field(nullable=True)
    first_name: Optional[Series[str]] = pa.Field(nullable=True)
    employment_id: Optional[Series[str]] = pa.Field(nullable=True)
    business_unit_id: Series[pd.Int64Dtype] = pa.Field(nullable=True)
    payment_method: Optional[Series[str]] = pa.Field(nullable=True, isin=[m.value for m in PaymentMethod])
    date_of_instant_registration: Optional[Series[datetime]] = pa.Field(nullable=True)
    instant_registration_uuid: Optional[Series[str]] = pa.Field(nullable=True)

    # Account fields (flattened)
    iban: Optional[Series[str]] = pa.Field(alias="account.iban", nullable=True)
    bic: Optional[Series[str]] = pa.Field(alias="account.bic", nullable=True)
    differing_account_holder: Optional[Series[str]] = pa.Field(alias="account.differing_account_holder", nullable=True)

    # Address fields (flattened)
    address_affix: Optional[Series[str]] = pa.Field(alias="address.address_affix", nullable=True)
    city: Optional[Series[str]] = pa.Field(alias="address.city", nullable=True)
    country: Optional[Series[str]] = pa.Field(alias="address.country", nullable=True, isin=[m.value for m in Country])
    house_number: Optional[Series[str]] = pa.Field(alias="address.house_number", nullable=True)
    postal_code: Optional[Series[str]] = pa.Field(alias="address.postal_code", nullable=True)
    street: Optional[Series[str]] = pa.Field(alias="address.street", nullable=True)

    # Activity fields (flattened)
    highest_level_of_professional_training: Series[pd.Int64Dtype] = pa.Field(alias="activity.highest_level_of_professional_training", nullable=True, isin=[m.value for m in HighestLevelOfProfessionalTraining])
    highest_level_of_education: Series[pd.Int64Dtype] = pa.Field(alias="activity.highest_level_of_education", nullable=True, isin=[m.value for m in HighestLevelOfEducation])
    allocation_of_working_hours_monday: Optional[Series[float]] = pa.Field(alias="activity.allocation_of_working_hours_monday", nullable=True)
    allocation_of_working_hours_tuesday: Optional[Series[float]] = pa.Field(alias="activity.allocation_of_working_hours_tuesday", nullable=True)
    allocation_of_working_hours_wednesday: Optional[Series[float]] = pa.Field(alias="activity.allocation_of_working_hours_wednesday", nullable=True)
    allocation_of_working_hours_thursday: Optional[Series[float]] = pa.Field(alias="activity.allocation_of_working_hours_thursday", nullable=True)
    allocation_of_working_hours_friday: Optional[Series[float]] = pa.Field(alias="activity.allocation_of_working_hours_friday", nullable=True)
    allocation_of_working_hours_saturday: Optional[Series[float]] = pa.Field(alias="activity.allocation_of_working_hours_saturday", nullable=True)
    allocation_of_working_hours_sunday: Optional[Series[float]] = pa.Field(alias="activity.allocation_of_working_hours_sunday", nullable=True)
    weekly_working_hours: Optional[Series[float]] = pa.Field(alias="activity.weekly_working_hours", nullable=True)
    individual_cost_center_id: Optional[Series[str]] = pa.Field(alias="activity.individual_cost_center_id", nullable=True)
    occupational_title: Optional[Series[str]] = pa.Field(alias="activity.occupational_title", nullable=True)
    job_carried_out: Optional[Series[str]] = pa.Field(alias="activity.job_carried_out", nullable=True)
    employee_type: Optional[Series[str]] = pa.Field(alias="activity.employee_type", nullable=True, isin=[m.value for m in EmployeeType])
    contractual_structure: Optional[Series[str]] = pa.Field(alias="activity.contractual_structure", nullable=True, isin=[m.value for m in ContractualStructure])
    # activity_type: Series[pd.Int64Dtype] = pa.Field(alias="activity.activity_type", nullable=True)
    department_id: Optional[Series[str]] = pa.Field(alias="activity.department_id", nullable=True)
    personnel_leasing: Series[pd.Int64Dtype] = pa.Field(alias="activity.personnel_leasing", nullable=True)

    # Personal Data fields (flattened)
    nationality: Optional[Series[str]] = pa.Field(alias="personal_data.nationality", nullable=True)
    sex: Optional[Series[str]] = pa.Field(alias="personal_data.sex", nullable=True, isin=[m.value for m in Sex])
    email: Optional[Series[str]] = pa.Field(alias="personal_data.email", nullable=True)
    phone: Optional[Series[str]] = pa.Field(alias="personal_data.phone", nullable=True)
    academic_title: Optional[Series[str]] = pa.Field(alias="personal_data.academic_title", nullable=True)
    birth_name: Optional[Series[str]] = pa.Field(alias="personal_data.birth_name", nullable=True)
    country_of_birth: Optional[Series[str]] = pa.Field(alias="personal_data.country_of_birth", nullable=True)
    date_of_birth: Optional[Series[datetime]] = pa.Field(alias="personal_data.date_of_birth", nullable=True)
    place_of_birth: Optional[Series[str]] = pa.Field(alias="personal_data.place_of_birth", nullable=True)
    work_permit: Optional[Series[datetime]] = pa.Field(alias="personal_data.work_permit", nullable=True)
    residency_permit: Optional[Series[datetime]] = pa.Field(alias="personal_data.residency_permit", nullable=True)
    certificate_of_study: Optional[Series[datetime]] = pa.Field(alias="personal_data.certificate_of_study", nullable=True)
    social_security_number: Optional[Series[str]] = pa.Field(alias="personal_data.social_security_number", nullable=True)
    european_social_security_number: Optional[Series[str]] = pa.Field(alias="personal_data.european_social_security_number", nullable=True)

    # Social Insurance fields (flattened)
    contribution_class_health_insurance: Series[pd.Int64Dtype] = pa.Field(alias="social_insurance.contribution_class_health_insurance", nullable=True, isin=[m.value for m in ContributionClassHealthInsurance])
    contribution_class_nursing_insurance: Series[pd.Int64Dtype] = pa.Field(alias="social_insurance.contribution_class_nursing_insurance", nullable=True)
    contribution_class_pension_insurance: Series[pd.Int64Dtype] = pa.Field(alias="social_insurance.contribution_class_pension_insurance", nullable=True, isin=[m.value for m in ContributionClassPensionInsurance])
    contribution_class_unemployment_insurance: Series[pd.Int64Dtype] = pa.Field(alias="social_insurance.contribution_class_unemployment_insurance", nullable=True)
    company_number_of_health_insurer: Optional[Series[str]] = pa.Field(alias="social_insurance.company_number_of_health_insurer", nullable=True)
    health_insurance_id: Series[pd.Int64Dtype] = pa.Field(alias="social_insurance.health_insurance_id", nullable=True)
    is_additional_contribution_to_nursing_insurance_for_childless_ignored: Optional[Series[bool]] = pa.Field(alias="social_insurance.is_additional_contribution_to_nursing_insurance_for_childless_ignored", nullable=True)
    # branch_office_of_health_insurer: Series[pd.Int64Dtype] = pa.Field(alias="social_insurance.branch_office_of_health_insurer", nullable=True)
    health_insurer_for_marginal_employee: Optional[Series[str]] = pa.Field(alias="social_insurance.health_insurer_for_marginal_employee", nullable=True)

    # Tax Card fields (flattened)
    annual_tax_allowance: Series[pd.Int64Dtype] = pa.Field(alias="tax_card.annual_tax_allowance", nullable=True)
    child_tax_allowances: Optional[Series[float]] = pa.Field(alias="tax_card.child_tax_allowances", nullable=True)
    denomination: Optional[Series[str]] = pa.Field(alias="tax_card.denomination", nullable=True, isin=[m.value for m in Denomination])
    factor: Optional[Series[float]] = pa.Field(alias="tax_card.factor", nullable=True)
    monthly_tax_allowance: Series[pd.Int64Dtype] = pa.Field(alias="tax_card.monthly_tax_allowance", nullable=True)
    spouses_denomination: Optional[Series[str]] = pa.Field(alias="tax_card.spouses_denomination", nullable=True, isin=[m.value for m in SpousesDenomination])
    tax_class: Optional[Series[str]] = pa.Field(alias="tax_card.tax_class", nullable=True)

    # Taxation fields (flattened)
    employment_type: Series[pd.Int64Dtype] = pa.Field(alias="taxation.employment_type", nullable=True, isin=[m.value for m in EmploymentType])
    requested_annual_allowance: Series[pd.Int64Dtype] = pa.Field(alias="taxation.requested_annual_allowance", nullable=True)
    tax_identification_number: Optional[Series[str]] = pa.Field(alias="taxation.tax_identification_number", nullable=True)
    flat_rate_tax: Series[pd.Int64Dtype] = pa.Field(alias="taxation.flat_rate_tax", nullable=True, isin=[m.value for m in FlatRateTax])

    # Vacation Entitlement fields (flattened)
    basic_vacation_entitlement: Optional[Series[float]] = pa.Field(alias="vacation_entitlement.basic_vacation_entitlement", nullable=True)

    # Vocational Training fields (flattened)
    # vocational_personnel_number: Series[pd.Int64Dtype] = pa.Field(alias="vocational_training.personnel_number", nullable=True)
    vocational_start: Optional[Series[datetime]] = pa.Field(alias="vocational_training.start", nullable=True)
    vocational_expected_end: Optional[Series[datetime]] = pa.Field(alias="vocational_training.expected_end", nullable=True)
    vocational_actual_end: Optional[Series[datetime]] = pa.Field(alias="vocational_training.actual_end", nullable=True)

    # We'd need to handle list fields differently - they'd typically be stored as strings or in separate tables
    # employment_periods, gross_payments, hourly_wages, individual_data - these would need special handling

    class Config:
        coerce = True

    class _Annotation:
        primary_keys = ["id"]


class EmploymentPeriodGet(BrynQPanderaDataFrameModel):
    """Schema for list of employment periods per employee"""

    # Parent link
    employee_id: Optional[Series[str]] = pa.Field(nullable=True)

    # Fields from EmploymentPeriod
    date_of_commencement_of_employment: Optional[Series[datetime]] = pa.Field(nullable=True)
    date_of_termination_of_employment: Optional[Series[datetime]] = pa.Field(nullable=True)

    class Config:
        coerce = True

    class _Annotation:
        primary_keys = ["employee_id", "date_of_commencement_of_employment"]


# Pydantic models for Employee creation/update operations

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


class Activity(BaseModel):
    model_config = ConfigDict(
        extra='allow',
    )
    highest_level_of_professional_training: (
        HighestLevelOfProfessionalTraining | None
    ) = None
    highest_level_of_education: HighestLevelOfEducation | None = None
    allocation_of_working_hours_monday: Annotated[
        float | None, Field(ge=0.0, le=24.0)
    ] = None
    allocation_of_working_hours_tuesday: Annotated[
        float | None, Field(ge=0.0, le=24.0)
    ] = None
    allocation_of_working_hours_wednesday: Annotated[
        float | None, Field(ge=0.0, le=24.0)
    ] = None
    allocation_of_working_hours_thursday: Annotated[
        float | None, Field(ge=0.0, le=24.0)
    ] = None
    allocation_of_working_hours_friday: Annotated[
        float | None, Field(ge=0.0, le=24.0)
    ] = None
    allocation_of_working_hours_saturday: Annotated[
        float | None, Field(ge=0.0, le=24.0)
    ] = None
    allocation_of_working_hours_sunday: Annotated[
        float | None, Field(ge=0.0, le=24.0)
    ] = None
    weekly_working_hours: Annotated[float | None, Field(ge=0.0, le=99.0)] = None
    individual_cost_center_id: Annotated[
        str | None,
        Field(
            max_length=13,
            pattern='^(([a-zA-Z0-9#][a-zA-Z0-9# ]{0,11}[a-zA-Z0-9#])|([a-zA-Z0-9#]){0,1})$',
        ),
    ] = None
    occupational_title: Annotated[
        str | None, Field(max_length=30, pattern='^[a-zA-Z0-9_]*$')
    ] = None
    job_carried_out: Annotated[
        str | None, Field(max_length=5, min_length=0, pattern='^[a-zA-Z0-9_]*$')
    ] = None
    employee_type: EmployeeType | None = None
    contractual_structure: ContractualStructure | None = None
    activity_type: Annotated[int | None, Field(ge=0, le=11)] = None
    department_id: Annotated[
        str | None, Field(max_length=8, pattern='^[a-zA-Z0-9_]*$')
    ] = None
    personnel_leasing: Annotated[int | None, Field(ge=0, le=2)] = None


class Address(BaseModel):
    model_config = ConfigDict(
        extra='allow',
    )
    address_affix: Annotated[str | None, Field(max_length=40)] = None
    city: Annotated[str | None, Field(max_length=34)] = None
    country: Country
    house_number: Annotated[str | None, Field(max_length=9)] = None
    postal_code: Annotated[str, Field(max_length=10)]
    street: Annotated[str | None, Field(max_length=33)] = None


class EmploymentPeriod(BaseModel):
    model_config = ConfigDict(
        extra='allow',
    )
    date_of_commencement_of_employment: datetime | None = None
    date_of_termination_of_employment: datetime | None = None


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


class IndividualData(BaseModel):
    model_config = ConfigDict(
        extra='allow',
    )
    id: Annotated[str | None, Field(max_length=5)] = None
    long_field_name: Annotated[str | None, Field(max_length=50)] = None
    short_field_name: Annotated[str | None, Field(max_length=8)] = None
    date: datetime | None = None
    amount: Annotated[float | None, Field(ge=-999999.99, le=999999.99)] = None
    long_field_name2: Annotated[str | None, Field(max_length=50)] = None
    short_field_name2: Annotated[str | None, Field(max_length=8)] = None
    date2: datetime | None = None
    amount2: Annotated[float | None, Field(ge=-999999.99, le=999999.99)] = None
    long_field_name3: Annotated[str | None, Field(max_length=50)] = None
    short_field_name3: Annotated[str | None, Field(max_length=8)] = None
    date3: datetime | None = None
    amount3: Annotated[float | None, Field(ge=-999999.99, le=999999.99)] = None
    long_field_name4: Annotated[str | None, Field(max_length=50)] = None
    short_field_name4: Annotated[str | None, Field(max_length=8)] = None
    date4: datetime | None = None
    amount4: Annotated[float | None, Field(ge=-999999.99, le=999999.99)] = None
    long_field_name5: Annotated[str | None, Field(max_length=50)] = None
    short_field_name5: Annotated[str | None, Field(max_length=8)] = None
    date5: datetime | None = None
    amount5: Annotated[float | None, Field(ge=-999999.99, le=999999.99)] = None
    long_field_name6: Annotated[str | None, Field(max_length=50)] = None
    short_field_name6: Annotated[str | None, Field(max_length=8)] = None
    date6: datetime | None = None
    amount6: Annotated[float | None, Field(ge=-999999.99, le=999999.99)] = None
    long_field_name7: Annotated[str | None, Field(max_length=50)] = None
    short_field_name7: Annotated[str | None, Field(max_length=8)] = None
    date7: datetime | None = None
    amount7: Annotated[float | None, Field(ge=-999999.99, le=999999.99)] = None
    long_field_name8: Annotated[str | None, Field(max_length=50)] = None
    short_field_name8: Annotated[str | None, Field(max_length=8)] = None
    date8: datetime | None = None
    amount8: Annotated[float | None, Field(ge=-999999.99, le=999999.99)] = None


class PersonalData(BaseModel):
    model_config = ConfigDict(
        extra='allow',
    )
    nationality: Annotated[str | None, Field(max_length=3, pattern='[0-9]{3}')] = None
    sex: Sex
    email: Annotated[
        str | None,
        Field(
            max_length=60,
            pattern='^[_a-zA-Z0-9\\-]+(\\.[_a-zA-Z0-9\\-]+)*@([a-zA-Z0-9]+(\\-[a-zA-Z0-9]+)*\\.)+([a-zA-Z]{2,})$',
        ),
    ] = None
    phone: Annotated[str | None, Field(max_length=60)] = None
    academic_title: Annotated[str | None, Field(max_length=20)] = None
    name_prefix: str | None = None
    name_affix: str | None = None
    birth_name: Annotated[str | None, Field(max_length=30)] = None
    birth_name_prefix: str | None = None
    birth_name_affix: str | None = None
    country_of_birth: Annotated[str | None, Field(max_length=3, pattern='[0-9]{3}')] = (
        None
    )
    date_of_birth: Annotated[
        datetime | None,
        Field(
            max_length=10,
            pattern='^(((17(([5][3-9])|[6-9]\\d))|((1[8-9]|[2-9]\\d)\\d\\d))-((((0[1-9])|1[012])-((0[1-9])|(1\\d)|(2[0-8])))|(((0[13456789])|1[012])-((29)|(30)))|(((0[13578])|1[02])-31)))|(((17(56|[68][048]|[79][26]))|((1[8-9]|[2-9]\\d)(0[48]|[2468][048]|[13579][26]))|((([2468][048]|[3579][26])00)))-02-29)|(((17(([5][3-9])|[6-9]\\d))|((1[8-9]|[2-9]\\d)\\d\\d))-((0[0-9]|1[012])-00))$',
        ),
    ] = None
    place_of_birth: Annotated[str | None, Field(max_length=34)] = None
    work_permit: Annotated[
        datetime | None,
        Field(
            max_length=10,
            pattern='^(((17(([5][3-9])|[6-9]\\d))|((1[8-9]|[2-9]\\d)\\d\\d))-((((0[1-9])|1[012])-((0[1-9])|(1\\d)|(2[0-8])))|(((0[13456789])|1[012])-((29)|(30)))|(((0[13578])|1[02])-31)))|(((17(56|[68][048]|[79][26]))|((1[8-9]|[2-9]\\d)(0[48]|[2468][048]|[13579][26]))|((([2468][048]|[3579][26])00)))-02-29)|(((17(([5][3-9])|[6-9]\\d))|((1[8-9]|[2-9]\\d)\\d\\d))-((0[0-9]|1[012])-00))$',
        ),
    ] = None
    residency_permit: Annotated[
        datetime | None,
        Field(
            max_length=10,
            pattern='^(((17(([5][3-9])|[6-9]\\d))|((1[8-9]|[2-9]\\d)\\d\\d))-((((0[1-9])|1[012])-((0[1-9])|(1\\d)|(2[0-8])))|(((0[13456789])|1[012])-((29)|(30)))|(((0[13578])|1[02])-31)))|(((17(56|[68][048]|[79][26]))|((1[8-9]|[2-9]\\d)(0[48]|[2468][048]|[13579][26]))|((([2468][048]|[3579][26])00)))-02-29)|(((17(([5][3-9])|[6-9]\\d))|((1[8-9]|[2-9]\\d)\\d\\d))-((0[0-9]|1[012])-00))$',
        ),
    ] = None
    certificate_of_study: Annotated[
        datetime | None,
        Field(
            max_length=10,
            pattern='^(((17(([5][3-9])|[6-9]\\d))|((1[8-9]|[2-9]\\d)\\d\\d))-((((0[1-9])|1[012])-((0[1-9])|(1\\d)|(2[0-8])))|(((0[13456789])|1[012])-((29)|(30)))|(((0[13578])|1[02])-31)))|(((17(56|[68][048]|[79][26]))|((1[8-9]|[2-9]\\d)(0[48]|[2468][048]|[13579][26]))|((([2468][048]|[3579][26])00)))-02-29)|(((17(([5][3-9])|[6-9]\\d))|((1[8-9]|[2-9]\\d)\\d\\d))-((0[0-9]|1[012])-00))$',
        ),
    ] = None
    social_security_number: Annotated[
        str | None,
        Field(
            max_length=12,
            pattern='^((\\d\\d)((([0-8]\\d)|([9][0-7]))([01]\\d)(\\d\\d))([A-Z])(\\d\\d)(\\d))$',
        ),
    ] = None
    european_social_security_number: Annotated[str | None, Field(max_length=20)] = None


class SocialInsurance(BaseModel):
    model_config = ConfigDict(
        extra='allow',
    )
    contribution_class_health_insurance: ContributionClassHealthInsurance
    contribution_class_nursing_insurance: Annotated[int, Field(ge=0, le=2)]
    contribution_class_pension_insurance: ContributionClassPensionInsurance
    contribution_class_unemployment_insurance: Annotated[int, Field(ge=0, le=2)]
    company_number_of_health_insurer: Annotated[str | None, Field(max_length=8)] = None
    health_insurance_id: Annotated[int | None, Field(ge=1, le=999)] = None
    is_additional_contribution_to_nursing_insurance_for_childless_ignored: bool
    branch_office_of_health_insurer: Annotated[int | None, Field(ge=1, le=9999)] = None
    health_insurer_for_marginal_employee: Annotated[str | None, Field(max_length=8)] = (
        None
    )


class TaxCard(BaseModel):
    model_config = ConfigDict(
        extra='allow',
    )
    annual_tax_allowance: Annotated[int | None, Field(ge=0, le=999999999)] = None
    child_tax_allowances: float | None = None
    denomination: Denomination | None = None
    factor: Annotated[float | None, Field(ge=0.001, le=0.999)] = None
    monthly_tax_allowance: Annotated[int | None, Field(ge=0, le=999999999)] = None
    spouses_denomination: SpousesDenomination | None = None
    tax_class: Annotated[str | None, Field(ge=0, le=6)] = None


class Taxation(BaseModel):
    model_config = ConfigDict(
        extra='allow',
    )
    employment_type: EmploymentType | None = None
    requested_annual_allowance: Annotated[int | None, Field(ge=0, le=999999999)] = None
    tax_identification_number: Annotated[
        str | None, Field(max_length=11, pattern='^([1-9]\\d{10})$')
    ] = None
    flat_rate_tax: FlatRateTax | None = None


class VacationEntitlement(BaseModel):
    model_config = ConfigDict(
        extra='allow',
    )
    basic_vacation_entitlement: Annotated[float | None, Field(ge=0.0, le=99.5)] = None


class VocationalTraining(BaseModel):
    model_config = ConfigDict(
        extra='allow',
    )
    personnel_number: int | None = None
    start: Annotated[
        datetime | None,
        Field(
            max_length=10,
            pattern='^(((17(([5][3-9])|[6-9]\\d))|((1[8-9]|[2-9]\\d)\\d\\d))-((((0[1-9])|1[012])-((0[1-9])|(1\\d)|(2[0-8])))|(((0[13456789])|1[012])-((29)|(30)))|(((0[13578])|1[02])-31)))|(((17(56|[68][048]|[79][26]))|((1[8-9]|[2-9]\\d)(0[48]|[2468][048]|[13579][26]))|((([2468][048]|[3579][26])00)))-02-29)|(((17(([5][3-9])|[6-9]\\d))|((1[8-9]|[2-9]\\d)\\d\\d))-((0[0-9]|1[012])-00))$',
        ),
    ] = None
    expected_end: Annotated[
        datetime | None,
        Field(
            max_length=10,
            pattern='^(((17(([5][3-9])|[6-9]\\d))|((1[8-9]|[2-9]\\d)\\d\\d))-((((0[1-9])|1[012])-((0[1-9])|(1\\d)|(2[0-8])))|(((0[13456789])|1[012])-((29)|(30)))|(((0[13578])|1[02])-31)))|(((17(56|[68][048]|[79][26]))|((1[8-9]|[2-9]\\d)(0[48]|[2468][048]|[13579][26]))|((([2468][048]|[3579][26])00)))-02-29)|(((17(([5][3-9])|[6-9]\\d))|((1[8-9]|[2-9]\\d)\\d\\d))-((0[0-9]|1[012])-00))$',
        ),
    ] = None
    actual_end: Annotated[
        datetime | None,
        Field(
            max_length=10,
            pattern='^(((17(([5][3-9])|[6-9]\\d))|((1[8-9]|[2-9]\\d)\\d\\d))-((((0[1-9])|1[012])-((0[1-9])|(1\\d)|(2[0-8])))|(((0[13456789])|1[012])-((29)|(30)))|(((0[13578])|1[02])-31)))|(((17(56|[68][048]|[79][26]))|((1[8-9]|[2-9]\\d)(0[48]|[2468][048]|[13579][26]))|((([2468][048]|[3579][26])00)))-02-29)|(((17(([5][3-9])|[6-9]\\d))|((1[8-9]|[2-9]\\d)\\d\\d))-((0[0-9]|1[012])-00))$',
        ),
    ] = None


class EmployeeCreate(BaseModel):
    model_config = ConfigDict(
        extra='allow',
    )
    surname: Annotated[str, Field(max_length=30)]
    client_id: Annotated[str | None, Field(max_length=13, pattern='\\d{7}-\\d{5}')] = (
        None
    )
    personnel_number: Annotated[int | None, Field(ge=1, le=99999)] = None
    company_personnel_number: Annotated[str | None, Field(max_length=20)] = None
    first_name: Annotated[str | None, Field(max_length=30)] = None
    employment_id: Annotated[str | None, Field(max_length=36)] = None
    business_unit_id: Annotated[int | None, Field(ge=0, le=9999)] = None
    payment_method: PaymentMethod | None = None
    date_of_instant_registration: datetime | None = None
    instant_registration_uuid: Annotated[
        UUID | None,
        Field(
            pattern='^[0-9a-fA-F]{8}\\b-[0-9a-fA-F]{4}\\b-[0-9a-fA-F]{4}\\b-[0-9a-fA-F]{4}\\b-[0-9a-fA-F]{12}$'
        ),
    ] = None
    activity: Activity | None = None
    account: Account | None = None
    address: Address | None = None
    employment_periods: Annotated[
        List[EmploymentPeriod] | None, Field(max_length=999)
    ] = None
    gross_payments: Annotated[List[GrossPayment] | None, Field(max_length=99)] = None
    hourly_wages: Annotated[List[HourlyWage] | None, Field(max_length=5)] = None
    individual_data: IndividualData | None = None
    personal_data: PersonalData | None = None
    social_insurance: SocialInsurance | None = None
    tax_card: TaxCard | None = None
    taxation: Taxation | None = None
    vacation_entitlement: VacationEntitlement | None = None
    vocational_training: VocationalTraining | None = None


class EmployeeUpdate(EmployeeCreate):
    """Employee model for update operations - inherits all fields from EmployeeCreate"""
    pass


# Models for list data that cannot be flattened
class EmploymentPeriod(BaseModel):
    """Employment period model for list validation"""
    model_config = ConfigDict(
        extra='allow',
    )
    date_of_commencement_of_employment: datetime | None = None
    date_of_termination_of_employment: datetime | None = None
