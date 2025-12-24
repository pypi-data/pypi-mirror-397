from datetime import datetime
from typing import Dict, Any, Optional, Tuple, List
import pandas as pd
from .base import BaseHrExchangeResource
from .schemas._api import JobResult
from .schemas.financial import HourlyWage, HourlyWageGet
from brynq_sdk_functions import Functions


class HourlyWages(BaseHrExchangeResource):
    """
    Hourly Wages resource for DATEV HR Exchange
    """

    def __init__(self, datev):
        super().__init__(datev)

    def get(
        self,
        personnel_number: Optional[int] = None,
        reference_date: Optional[datetime] = None
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get hourly wages via job processing

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
            print(f"Creating job to fetch hourly wages for date: {reference_date_str}")

        job_result = self._create_and_wait_for_job(
            resource_name="hourly-wages",
            resource_id=str(personnel_number) if personnel_number else None,
            reference_date=reference_date_str
        )

        wages_data = job_result.exchangeObjects or []

        # Inject employee_id into rows
        rows = []
        for obj in wages_data:
            row = dict(obj)
            if 'employee_id' not in row:
                row['employee_id'] = obj.get('employee_id') or obj.get('id') or (
                    str(personnel_number) if personnel_number else None
                )
            rows.append(row)

        df = pd.json_normalize(rows) if rows else pd.DataFrame()
        valid_data, invalid_data = Functions.validate_data(df, HourlyWageGet, debug=self.debug)
        return valid_data, invalid_data

    def create(
        self,
        personnel_number: int,
        wages_data: Dict[str, Any] | List[Dict[str, Any]],
        reference_date: Optional[datetime] = None
    ) -> JobResult:
        """
        Create one or more hourly wages.
        """
        reference_date = reference_date or datetime.now()

        # Normalize to list and validate
        if isinstance(wages_data, dict):
            payload_list = [wages_data]
        else:
            payload_list = list(wages_data)

        validated_list = [self._validate_request_data(item, HourlyWage) for item in payload_list]

        endpoint = f"clients/{self.datev.client_id}/employees/{personnel_number}/hourly-wages"
        params = {"reference-date": reference_date.strftime("%Y-%m-%d")}

        if self.debug:
            print(f"Creating hourly wage(s) for employee {personnel_number}: {validated_list}")

        response = self._make_request(endpoint, method="POST", json_data=validated_list, params=params)

        if isinstance(response, dict) and ("id" in response or "job_id" in response):
            job_uuid = str(response.get("id", response.get("job_id")))
            self._wait_for_job(job_uuid)
            return self._get_job_result(job_uuid)

        return JobResult(exchangeObjects=[response] if response else [])

    def update(
        self,
        personnel_number: int,
        hourly_wage_id: int,
        wage_data: Dict[str, Any],
        reference_date: Optional[datetime] = None
    ) -> JobResult:
        """
        Update an hourly wage

        Args:
            personnel_number: Personnel number of employee
            hourly_wage_id: Hourly wage ID
            wage_data: Updated hourly wage data
            reference_date: Optional reference date
            max_wait_time: Maximum time to wait for job completion
            poll_interval: How often to check job status

        Returns:
            JobResult object
        """
        reference_date = reference_date or datetime.now()

        # Validate wage data
        validated_data = self._validate_request_data(wage_data, HourlyWage)

        endpoint = f"clients/{self.datev.client_id}/employees/{personnel_number}/hourly-wages/{hourly_wage_id}"
        params = {"reference-date": reference_date.strftime("%Y-%m-%d")}

        if self.debug:
            print(f"Updating hourly wage {hourly_wage_id} for employee {personnel_number}: {validated_data}")

        response = self._make_request(endpoint, method="PUT", json_data=validated_data, params=params)

        if isinstance(response, dict) and ("id" in response or "job_id" in response):
            job_uuid = str(response.get("id", response.get("job_id")))
            self._wait_for_job(job_uuid)
            return self._get_job_result(job_uuid)

        return JobResult(exchangeObjects=[response] if response else [])
