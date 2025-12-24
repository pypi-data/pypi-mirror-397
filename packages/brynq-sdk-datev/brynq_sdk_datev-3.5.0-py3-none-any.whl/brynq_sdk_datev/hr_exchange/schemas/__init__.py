# Import all models for backward compatibility
# This ensures existing code that imports from this module continues to work

# Import all enums
from ._enums import *

# Import employee models
from .employee import (
    EmployeeGet, EmployeeCreate, EmployeeUpdate, PersonalData, Activity,
    EmploymentPeriod, EmploymentPeriodGet, Address, VacationEntitlement,
    VocationalTraining, IndividualData
)

# Import financial models
from .financial import (
    GrossPaymentCreate, GrossPaymentGet, HourlyWageGet
)

# Import tax and insurance models
from .tax_insurance import (
    SocialInsurance, TaxCard, Taxation
)

# Import absence models
from .absences import (
    AbsenceLug, AbsenceLodas, AbsenceLugGet, AbsenceLodasGet
)

# Import organizational models
from .organizational import (
    ClientGet, SalaryTypeGet, DepartmentGet, CostCenterGet,
    HealthInsurerGet, BusinessUnitGet
)

# Import record models
from .individual_data import (
    IndividualDataGet
)

# Import monthly records models
from .monthly_records import (
    MonthRecord, MonthRecordGet
)

# Import API models
from ._api import (
    Job, JobResult, Error, AdditionalError, ErrorMessage5xx,
    Resource, RestHook, RestHookResourceInfo, ExchangeObject
)

__all__ = [
    # Employee models
    'EmployeeGet', 'EmployeeCreate', 'EmployeeUpdate', 'PersonalData', 'Activity',
    'EmploymentPeriod', 'EmploymentPeriodGet', 'Address', 'VacationEntitlement',
    'VocationalTraining', 'IndividualData',
    # Financial models
    'GrossPaymentCreate', 'GrossPaymentGet', 'HourlyWageGet',
    # Tax & Insurance models
    'SocialInsurance', 'TaxCard', 'Taxation',
    # Absence models
    'AbsenceLug', 'AbsenceLodas', 'AbsenceLugGet', 'AbsenceLodasGet',
    # Organizational models
    'ClientGet', 'SalaryTypeGet', 'DepartmentGet', 'CostCenterGet',
    'HealthInsurerGet', 'BusinessUnitGet',
    # Record models
    'IndividualDataGet', 'MonthRecord', 'MonthRecordGet',
    # API models
    'Job', 'JobResult', 'Error', 'AdditionalError', 'ErrorMessage5xx',
    'Resource', 'RestHook', 'RestHookResourceInfo', 'ExchangeObject',
]
