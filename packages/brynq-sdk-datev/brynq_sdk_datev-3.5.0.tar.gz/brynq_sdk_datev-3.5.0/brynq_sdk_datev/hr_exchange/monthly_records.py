from datetime import datetime
from typing import Dict, Any, Optional, Tuple, List, Union
import pandas as pd
from .base import BaseHrExchangeResource
from .schemas._api import JobResult
from .schemas.monthly_records import MonthRecordGet, MonthRecord
from brynq_sdk_functions import Functions


class MonthRecords(BaseHrExchangeResource):
    """
    Month Records resource for DATEV HR Exchange
    """

    def __init__(self, datev):
        super().__init__(datev)

    def get(
        self,
        personnel_number: Optional[int] = None,
        reference_date: Optional[datetime] = None
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get month records via job processing (all or per employee).

        Args:
            personnel_number: Optional personnel number to filter for specific employee
            reference_date: Optional reference date
            max_wait_time: Maximum time to wait for job completion
            poll_interval: How often to check job status

        Returns:
            Tuple of (valid_data, invalid_data) DataFrames
        """
        reference_date = reference_date or datetime.now()
        reference_date_str = reference_date.strftime("%Y-%m-%d")

        if self.debug:
            who = f"employee {personnel_number}" if personnel_number else "all employees"
            print(f"Creating job to fetch month records for {who} at {reference_date_str}")

        job_result = self._create_and_wait_for_job(
            resource_name="month-records",
            resource_id=str(personnel_number) if personnel_number else None,
            reference_date=reference_date_str
        )

        records_data = job_result.exchangeObjects or []

        rows = []
        for obj in records_data:
            row = dict(obj)
            # If the API response nests records under employees, try to lift and inject employee_id
            employee_id = obj.get('employee_id') or obj.get('id')
            row['employee_id'] = employee_id
            rows.append(row)

        df = pd.json_normalize(rows) if rows else pd.DataFrame()
        valid_data, invalid_data = Functions.validate_data(df, MonthRecordGet, debug=self.debug)
        return valid_data, invalid_data

    def create(
        self,
        records_data: Union[Dict[str, Any], List[Dict[str, Any]]],
        personnel_number: Optional[int] = None,
        reference_date: Optional[datetime] = None
    ) -> JobResult:
        """
        Create month record(s). If personnel_number is provided, post to the employee endpoint;
        otherwise post in bulk at client level.

        Args:
            records_data: Single month record dict or list of month record dicts
            personnel_number: Optional personnel number (single-employee post)
            reference_date: Optional reference date
            max_wait_time: Maximum time to wait for job completion
            poll_interval: How often to check job status

        Returns:
            JobResult object
        """
        reference_date = reference_date or datetime.now()

        params = {"reference-date": reference_date.strftime("%Y-%m-%d")}

        # Normalize to list
        payload_list: List[Dict[str, Any]]
        if isinstance(records_data, dict):
            payload_list = [records_data]
        else:
            payload_list = list(records_data)

        # Validate outgoing data
        validated_list: List[Dict[str, Any]] = []
        for item in payload_list:
            # If posting at client level, ensure personnel_number is present in each record
            if personnel_number is None and "personnel_number" not in item:
                raise ValueError("Each month record must include 'personnel_number' when posting at client level.")
            validated = self._validate_request_data(item, MonthRecord)
            # If posting for a specific employee and the record lacks personnel_number, set it
            if personnel_number is not None and not validated.get("personnel_number"):
                validated["personnel_number"] = personnel_number
            validated_list.append(validated)

        if personnel_number is not None:
            endpoint = f"clients/{self.datev.client_id}/employees/{personnel_number}/month-records"
            json_payload: Union[Dict[str, Any], List[Dict[str, Any]]] = validated_list
        else:
            endpoint = f"clients/{self.datev.client_id}/month-records"
            json_payload = validated_list

        if self.debug:
            scope = f"employee {personnel_number}" if personnel_number is not None else "client level"
            print(f"Creating month record(s) at {scope}: {json_payload}")

        response = self._make_request(endpoint, method="POST", json_data=json_payload, params=params)

        if isinstance(response, dict) and ("id" in response or "job_id" in response):
            job_uuid = str(response.get("id", response.get("job_id")))
            self._wait_for_job(job_uuid)
            return self._get_job_result(job_uuid)

        return JobResult(exchangeObjects=[response] if response else [])
