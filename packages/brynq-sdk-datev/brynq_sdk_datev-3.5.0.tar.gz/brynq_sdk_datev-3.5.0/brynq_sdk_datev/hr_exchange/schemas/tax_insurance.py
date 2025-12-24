# Tax and Social Insurance models for HR Exchange
# This file contains tax and social insurance related models

from pydantic import BaseModel, ConfigDict, Field
from typing import Annotated
from ._enums import (
    ContributionClassHealthInsurance, ContributionClassPensionInsurance,
    Denomination, SpousesDenomination, EmploymentType, FlatRateTax
)


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
