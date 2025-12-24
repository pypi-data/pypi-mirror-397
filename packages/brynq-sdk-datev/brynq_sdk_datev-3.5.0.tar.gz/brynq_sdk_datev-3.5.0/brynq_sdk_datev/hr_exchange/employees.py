from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple, NamedTuple
import pandas as pd
from .base import BaseHrExchangeResource
from .schemas.employee import EmployeeGet, EmploymentPeriodGet
from .schemas.financial import GrossPaymentGet, HourlyWageGet
from .schemas._api import JobResult, Resource
from brynq_sdk_functions import Functions


class Employees(BaseHrExchangeResource):
    """
    Employees resource for DATEV HR Exchange
    Handles employee data operations via jobs and direct API calls
    """

    def __init__(self, datev):
        super().__init__(datev)

    class EmployeeDataResult(NamedTuple):
        core: Tuple[pd.DataFrame, pd.DataFrame]
        employment_periods: Tuple[pd.DataFrame, pd.DataFrame]
        gross_payments: Tuple[pd.DataFrame, pd.DataFrame]
        hourly_wages: Tuple[pd.DataFrame, pd.DataFrame]

    def get(
        self,
        personnel_number: Optional[int] = None,
        reference_date: Optional[datetime] = None
    ) -> EmployeeDataResult:
        """
        Get employee data via job-based processing (for bulk operations)

        Args:
            personnel_number: Optional personnel number for specific employee
            reference_date: Optional reference date
            max_wait_time: Maximum time to wait for job completion
            poll_interval: How often to check job status

        Returns:
            Tuple of (valid_data, invalid_data) DataFrames
        """
        reference_date = reference_date or datetime.now()
        reference_date_str = reference_date.strftime("%Y-%m")

        if self.debug:
            print(f"Creating job to fetch employees for date: {reference_date_str}")

        # Create job and wait for result using new API structure
        job_result = self._create_and_wait_for_job(
            resource_name="employees",
            resource_id=str(personnel_number) if personnel_number else None,
            reference_date=reference_date_str
        )

        # Extract employees data from job result
        raw_employees = []
        if job_result.exchangeObjects:
            raw_employees = job_result.exchangeObjects

        if not raw_employees:
            empty_df = pd.DataFrame()
            return Employees.EmployeeDataResult(
                core=(empty_df, empty_df),
                employment_periods=(empty_df, empty_df),
                gross_payments=(empty_df, empty_df),
                hourly_wages=(empty_df, empty_df),
            )

        # Core employee data: strip list fields, keep rest flattened via EmployeeGet
        core_list_fields = ['employment_periods', 'gross_payments', 'hourly_wages']
        core_employees = []
        for emp in raw_employees:
            core = {k: v for k, v in emp.items() if k not in core_list_fields}
            core_employees.append(core)

        core_df = pd.json_normalize(core_employees)
        core_valid, core_invalid = Functions.validate_data(core_df, EmployeeGet, debug=self.debug)

        # Helper to extract list items with employee_id injected
        def extract_list(list_field: str) -> List[dict]:
            items: List[dict] = []
            for emp in raw_employees:
                employee_id = emp.get('employee_id') or emp.get('id')
                for item in emp.get(list_field, []) or []:
                    row = dict(item)
                    row['employee_id'] = employee_id
                    items.append(row)
            return items

        # Employment periods
        ep_items = extract_list('employment_periods')
        if ep_items:
            ep_df = pd.json_normalize(ep_items)
            ep_valid, ep_invalid = Functions.validate_data(ep_df, EmploymentPeriodGet, debug=self.debug)
        else:
            ep_valid = ep_invalid = pd.DataFrame()

        # Gross payments
        gp_items = extract_list('gross_payments')
        if gp_items:
            gp_df = pd.json_normalize(gp_items)
            gp_valid, gp_invalid = Functions.validate_data(gp_df, GrossPaymentGet, debug=self.debug)
        else:
            gp_valid = gp_invalid = pd.DataFrame()

        # Hourly wages
        hw_items = extract_list('hourly_wages')
        if hw_items:
            hw_df = pd.json_normalize(hw_items)
            hw_valid, hw_invalid = Functions.validate_data(hw_df, HourlyWageGet, debug=self.debug)
        else:
            hw_valid = hw_invalid = pd.DataFrame()

        return Employees.EmployeeDataResult(
            core=(core_valid, core_invalid),
            employment_periods=(ep_valid, ep_invalid),
            gross_payments=(gp_valid, gp_invalid),
            hourly_wages=(hw_valid, hw_invalid),
        )

    def create(
        self,
        employee_data: Dict[str, Any],
        reference_date: Optional[datetime] = None
    ) -> JobResult:
        """
        Create a new employee via job processing

        Args:
            employee_data: Employee data to create
            reference_date: Optional reference date
            max_wait_time: Maximum time to wait for job completion
            poll_interval: How often to check job status

        Returns:
            JobResult object
        """
        reference_date = reference_date or datetime.now()

        # Validate employee data using EmployeeCreate model
        from .schemas import EmployeeCreate
        validated_data = self._validate_request_data(employee_data, EmployeeCreate)

        endpoint = f"clients/{self.datev.client_id}/employees"
        params = {"reference-date": reference_date.strftime("%Y-%m")}

        if self.debug:
            print(f"Creating employee with data: {validated_data}")

        # Create employee directly - this may return a job or direct response
        response = self._make_request(endpoint, method="POST", json_data=validated_data, params=params)

        # If response contains a job ID, wait for completion
        if isinstance(response, dict) and ("id" in response or "job_id" in response):
            job_uuid = str(response.get("id", response.get("job_id")))
            self._wait_for_job(job_uuid)
            return self._get_job_result(job_uuid)

        # Otherwise return response as JobResult-like structure
        return JobResult(exchangeObjects=[response] if response else [])

    def update(
        self,
        personnel_number: int,
        employee_data: Dict[str, Any],
        reference_date: Optional[datetime] = None
    ) -> JobResult:
        """
        Update an employee via job processing

        Args:
            personnel_number: Personnel number of employee to update
            employee_data: Updated employee data
            reference_date: Optional reference date
            max_wait_time: Maximum time to wait for job completion
            poll_interval: How often to check job status

        Returns:
            JobResult object
        """
        reference_date = reference_date or datetime.now()

        # Validate employee data using EmployeeUpdate model
        from .schemas import EmployeeUpdate
        validated_data = self._validate_request_data(employee_data, EmployeeUpdate)

        endpoint = f"clients/{self.datev.client_id}/employees/{personnel_number}"
        params = {"reference-date": reference_date.strftime("%Y-%m")}

        if self.debug:
            print(f"Updating employee {personnel_number} with data: {validated_data}")

        # Update employee - this may return a job or direct response
        response = self._make_request(endpoint, method="PUT", json_data=validated_data, params=params)

        # If response contains a job ID, wait for completion
        if isinstance(response, dict) and ("id" in response or "job_id" in response):
            job_uuid = str(response.get("id", response.get("job_id")))
            self._wait_for_job(job_uuid)
            return self._get_job_result(job_uuid)

        # Otherwise return response as JobResult-like structure
        return JobResult(exchangeObjects=[response] if response else [])

    # Delete is not supported for Employees in HR Exchange API
