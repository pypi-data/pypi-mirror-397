from datetime import datetime
from typing import Dict, Any, Optional, Tuple
import pandas as pd
from .base import BaseHrExchangeResource
from .schemas._api import JobResult
from brynq_sdk_functions import Functions
from .schemas.employee import EmploymentPeriodGet


class EmploymentPeriods(BaseHrExchangeResource):
    """
    Employment Periods resource for DATEV HR Exchange
    """

    def __init__(self, datev):
        super().__init__(datev)

    def get(
        self,
        personnel_number: int,
        employment_period_date: Optional[str] = None,
        reference_date: Optional[datetime] = None
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get employment periods via job processing

        Args:
            personnel_number: Personnel number of employee
            employment_period_date: Optional specific employment period date (YYYY-MM-DD)
            reference_date: Optional reference date
            max_wait_time: Maximum time to wait for job completion
            poll_interval: How often to check job status

        Returns:
            Tuple of (valid_data, invalid_data) DataFrames
        """
        reference_date = reference_date or datetime.now()

        path = f"/clients/{self.datev.client_id}/employees/{personnel_number}/employment-periods"
        if employment_period_date:
            path += f"/{employment_period_date}"

        if self.debug:
            print(f"Creating job to fetch employment periods for employee {personnel_number}")

        job_result = self._create_and_wait_for_job(
            resource_name="employment-periods",
            resource_id=str(personnel_number) if personnel_number else None,
            reference_date=reference_date.strftime("%Y-%m")
        )

        periods_data = job_result.exchangeObjects or []

        rows = []
        for obj in periods_data:
            row = dict(obj)
            if 'employee_id' not in row:
                row['employee_id'] = str(personnel_number)
            rows.append(row)

        df = pd.json_normalize(rows) if rows else pd.DataFrame()
        valid_data, invalid_data = Functions.validate_data(df, EmploymentPeriodGet, debug=self.debug)
        return valid_data, invalid_data

    def create(
        self,
        personnel_number: int,
        period_data: Dict[str, Any],
        reference_date: Optional[datetime] = None
    ) -> JobResult:
        """
        Create an employment period

        Args:
            personnel_number: Personnel number of employee
            period_data: Employment period data
            reference_date: Optional reference date
            max_wait_time: Maximum time to wait for job completion
            poll_interval: How often to check job status

        Returns:
            JobResult object
        """
        reference_date = reference_date or datetime.now()

        endpoint = f"clients/{self.datev.client_id}/employees/{personnel_number}/employment-periods"
        params = {"reference-date": reference_date.strftime("%Y-%m-%d")}

        if self.debug:
            print(f"Creating employment period for employee {personnel_number}: {period_data}")

        response = self._make_request(endpoint, method="POST", json_data=period_data, params=params)

        if isinstance(response, dict) and ("id" in response or "job_id" in response):
            job_uuid = str(response.get("id", response.get("job_id")))
            self._wait_for_job(job_uuid)
            return self._get_job_result(job_uuid)

        return JobResult(exchangeObjects=[response] if response else [])

    def update(
        self,
        personnel_number: int,
        employment_period_date: str,
        period_data: Dict[str, Any],
        reference_date: Optional[datetime] = None
    ) -> JobResult:
        """
        Update an employment period

        Args:
            personnel_number: Personnel number of employee
            employment_period_date: Employment period date (YYYY-MM-DD)
            period_data: Updated employment period data
            reference_date: Optional reference date
            max_wait_time: Maximum time to wait for job completion
            poll_interval: How often to check job status

        Returns:
            JobResult object
        """
        reference_date = reference_date or datetime.now()

        endpoint = f"clients/{self.datev.client_id}/employees/{personnel_number}/employment-periods/{employment_period_date}"
        params = {"reference-date": reference_date.strftime("%Y-%m-%d")}

        if self.debug:
            print(f"Updating employment period {employment_period_date} for employee {personnel_number}: {period_data}")

        response = self._make_request(endpoint, method="PUT", json_data=period_data, params=params)

        if isinstance(response, dict) and ("id" in response or "job_id" in response):
            job_uuid = str(response.get("id", response.get("job_id")))
            self._wait_for_job(job_uuid)
            return self._get_job_result(job_uuid)

        return JobResult(exchangeObjects=[response] if response else [])

    def delete(
        self,
        personnel_number: int,
        employment_period_date: str,
        reference_date: Optional[datetime] = None
    ) -> JobResult:
        """
        Delete an employment period

        Args:
            personnel_number: Personnel number of employee
            employment_period_date: Employment period date (YYYY-MM-DD)
            reference_date: Optional reference date
            max_wait_time: Maximum time to wait for job completion
            poll_interval: How often to check job status

        Returns:
            JobResult object
        """
        reference_date = reference_date or datetime.now()

        endpoint = f"clients/{self.datev.client_id}/employees/{personnel_number}/employment-periods/{employment_period_date}"
        params = {"reference-date": reference_date.strftime("%Y-%m-%d")}

        if self.debug:
            print(f"Deleting employment period {employment_period_date} for employee {personnel_number}")

        response = self._make_request(endpoint, method="DELETE", params=params)

        if isinstance(response, dict) and ("id" in response or "job_id" in response):
            job_uuid = str(response.get("id", response.get("job_id")))
            self._wait_for_job(job_uuid)
            return self._get_job_result(job_uuid)

        return JobResult(exchangeObjects=[] if not response else [response])
