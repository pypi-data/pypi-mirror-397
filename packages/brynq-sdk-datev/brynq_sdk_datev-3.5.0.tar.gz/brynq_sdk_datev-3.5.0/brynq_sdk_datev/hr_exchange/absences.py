from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
import pandas as pd
from .base import BaseHrExchangeResource
from .schemas._api import JobResult
from .schemas.absences import AbsenceLugGet, AbsenceLodasGet, AbsenceLug, AbsenceLodas
from brynq_sdk_functions import Functions


class Absences(BaseHrExchangeResource):
    """
    Absences resource for DATEV HR Exchange
    Handles absence data for both LUG and LODAS systems
    """

    def __init__(self, datev, mode: str = "lodas"):
        super().__init__(datev)
        mode_lower = (mode or "lodas").lower()
        if mode_lower not in ("lodas", "lug"):
            raise ValueError("mode must be 'lodas' or 'lug'")
        self.mode = mode_lower

    def get(
        self,
        personnel_number: Optional[int] = None,
        reference_date: Optional[datetime] = None
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get absences via job processing for either LODAS (default) or LuG, based on init mode.

        Args:
            personnel_number: Optional personnel number; when provided, fetches for that employee
            reference_date: Optional reference date
            max_wait_time: Maximum time to wait for job completion
            poll_interval: How often to check job status

        Returns:
            Tuple of (valid_data, invalid_data) DataFrames
        """
        reference_date = reference_date or datetime.now()
        reference_date_str = reference_date.strftime("%Y-%m-%d")

        # Build path based on mode
        mode_segment = "lodas" if self.mode == "lodas" else "lug"
        if personnel_number is None:
            raise ValueError("personnel_number must be provided to fetch absences in HR Exchange")

        path = f"/clients/{self.datev.client_id}/employees/{personnel_number}/absences/{mode_segment}"

        resource_data = {
            "resource": {
                "path": path,
                "resourceType": "absences",
                "reference_date": reference_date_str,
            }
        }

        if self.debug:
            print(f"Creating job to fetch {mode_segment.upper()} absences: {resource_data}")

        job_result = self._create_and_wait_for_job(
            resource_name="absences",
            resource_id=str(personnel_number) if personnel_number else None,
            reference_date=reference_date.strftime("%Y-%m")
        )

        absences_data = job_result.exchangeObjects or []
        df = pd.json_normalize(absences_data) if absences_data else pd.DataFrame()

        # Validate with schema per mode
        if self.mode == "lodas":
            valid, invalid = Functions.validate_data(df, AbsenceLodasGet, debug=self.debug)
        else:
            valid, invalid = Functions.validate_data(df, AbsenceLugGet, debug=self.debug)

        return valid, invalid

    def create(
        self,
        personnel_number: int,
        absences_data: List[Dict[str, Any]] | Dict[str, Any],
        reference_date: Optional[datetime] = None
    ) -> JobResult:
        """
        Create absence(s) for the configured mode (lodas|lug).

        Args:
            personnel_number: Employee personnel number
            absences_data: Single absence dict or list of absence dicts
            reference_date: Optional reference date
            max_wait_time: Maximum time to wait for job completion
            poll_interval: How often to check job status

        Returns:
            JobResult
        """
        reference_date = reference_date or datetime.now()

        mode_segment = "lodas" if self.mode == "lodas" else "lug"
        endpoint = f"clients/{self.datev.client_id}/employees/{personnel_number}/absences/{mode_segment}"
        params = {"reference-date": reference_date.strftime("%Y-%m-%d")}

        # Normalize to list
        if isinstance(absences_data, dict):
            payload_list = [absences_data]
        else:
            payload_list = list(absences_data)

        # Validate per mode
        schema_class = AbsenceLodas if self.mode == "lodas" else AbsenceLug
        validated_list: List[Dict[str, Any]] = [
            self._validate_request_data(item, schema_class) for item in payload_list
        ]

        if self.debug:
            print(f"Creating {self.mode.upper()} absences for employee {personnel_number}: {validated_list}")

        response = self._make_request(endpoint, method="POST", json_data=validated_list, params=params)

        if isinstance(response, dict) and ("id" in response or "job_id" in response):
            job_uuid = str(response.get("id", response.get("job_id")))
            self._wait_for_job(job_uuid)
            return self._get_job_result(job_uuid)

        return JobResult(exchangeObjects=[response] if response else [])

    def delete(
        self,
        personnel_number: int,
        absence_identifier: str,
        reference_date: Optional[datetime] = None
    ) -> JobResult:
        """
        Delete an absence, mapping identifier field according to mode.

        Args:
            personnel_number: Employee personnel number
            absence_identifier: For LuG: absence_id; For LODAS: absence_start_date (YYYY-MM-DD)
            reference_date: Optional reference date
            max_wait_time: Maximum time to wait for job completion
            poll_interval: How often to check job status
        """
        reference_date = reference_date or datetime.now()
        mode_segment = "lodas" if self.mode == "lodas" else "lug"
        endpoint = (
            f"clients/{self.datev.client_id}/employees/{personnel_number}/absences/{mode_segment}/{absence_identifier}"
        )
        params = {"reference-date": reference_date.strftime("%Y-%m-%d")}

        if self.debug:
            print(f"Deleting {self.mode.upper()} absence {absence_identifier} for employee {personnel_number}")

        response = self._make_request(endpoint, method="DELETE", params=params)

        if isinstance(response, dict) and ("id" in response or "job_id" in response):
            job_uuid = str(response.get("id", response.get("job_id")))
            self._wait_for_job(job_uuid)
            return self._get_job_result(job_uuid)

        return JobResult(exchangeObjects=[] if not response else [response])
