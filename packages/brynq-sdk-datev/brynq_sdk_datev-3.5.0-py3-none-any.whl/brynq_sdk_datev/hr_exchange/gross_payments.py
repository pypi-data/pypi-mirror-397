from datetime import datetime
from typing import Dict, Any, Optional, Tuple
import pandas as pd
from .base import BaseHrExchangeResource
from .schemas._api import JobResult
from .schemas.financial import GrossPayment, GrossPaymentGet
from brynq_sdk_functions import Functions


class GrossPayments(BaseHrExchangeResource):
    """
    Gross Payments resource for DATEV HR Exchange
    """

    def __init__(self, datev):
        super().__init__(datev)

    def get(
        self,
        personnel_number: int,
        gross_payment_id: Optional[int] = None,
        reference_date: Optional[datetime] = None
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get gross payments via job processing

        Args:
            personnel_number: Personnel number of employee
            gross_payment_id: Optional specific gross payment ID
            reference_date: Optional reference date
            max_wait_time: Maximum time to wait for job completion
            poll_interval: How often to check job status

        Returns:
            Tuple of (valid_data, invalid_data) DataFrames
        """
        reference_date = reference_date or datetime.now()

        path = f"/clients/{self.datev.client_id}/employees/{personnel_number}/gross-payments"
        if gross_payment_id:
            path += f"/{gross_payment_id}"


        if self.debug:
            print(f"Creating job to fetch gross payments for employee {personnel_number}")

        job_result = self._create_and_wait_for_job(
            resource_name="gross-payments",
            resource_id=str(personnel_number) if personnel_number else None,
            reference_date=reference_date.strftime("%Y-%m")
        )

        payments_data = job_result.exchangeObjects or []

        # Inject employee_id where available (parent context or object)
        rows = []
        for obj in payments_data:
            row = dict(obj)
            if 'employee_id' not in row:
                row['employee_id'] = obj.get('employee_id') or obj.get('id') or str(personnel_number)
            rows.append(row)

        df = pd.json_normalize(rows) if rows else pd.DataFrame()
        valid_data, invalid_data = Functions.validate_data(df, GrossPaymentGet, debug=self.debug)
        return valid_data, invalid_data

    def create(
        self,
        personnel_number: int,
        payment_data: Dict[str, Any],
        reference_date: Optional[datetime] = None
    ) -> JobResult:
        """
        Create a gross payment

        Args:
            personnel_number: Personnel number of employee
            payment_data: Gross payment data
            reference_date: Optional reference date
            max_wait_time: Maximum time to wait for job completion
            poll_interval: How often to check job status

        Returns:
            JobResult object
        """
        reference_date = reference_date or datetime.now()

        # Validate payment data
        validated_data = self._validate_request_data(payment_data, GrossPayment)

        endpoint = f"clients/{self.datev.client_id}/employees/{personnel_number}/gross-payments"
        params = {"reference-date": reference_date.strftime("%Y-%m-%d")}

        if self.debug:
            print(f"Creating gross payment for employee {personnel_number}: {validated_data}")

        response = self._make_request(endpoint, method="POST", json_data=validated_data, params=params)

        if isinstance(response, dict) and ("id" in response or "job_id" in response):
            job_uuid = str(response.get("id", response.get("job_id")))
            self._wait_for_job(job_uuid)
            return self._get_job_result(job_uuid)

        return JobResult(exchangeObjects=[response] if response else [])

    def update(
        self,
        personnel_number: int,
        gross_payment_id: int,
        payment_data: Dict[str, Any],
        reference_date: Optional[datetime] = None
    ) -> JobResult:
        """
        Update a gross payment

        Args:
            personnel_number: Personnel number of employee
            gross_payment_id: Gross payment ID
            payment_data: Updated gross payment data
            reference_date: Optional reference date
            max_wait_time: Maximum time to wait for job completion
            poll_interval: How often to check job status

        Returns:
            JobResult object
        """
        reference_date = reference_date or datetime.now()

        # Validate payment data
        validated_data = self._validate_request_data(payment_data, GrossPayment)

        endpoint = f"clients/{self.datev.client_id}/employees/{personnel_number}/gross-payments/{gross_payment_id}"
        params = {"reference-date": reference_date.strftime("%Y-%m-%d")}

        if self.debug:
            print(f"Updating gross payment {gross_payment_id} for employee {personnel_number}: {validated_data}")

        response = self._make_request(endpoint, method="PUT", json_data=validated_data, params=params)

        if isinstance(response, dict) and ("id" in response or "job_id" in response):
            job_uuid = str(response.get("id", response.get("job_id")))
            self._wait_for_job(job_uuid)
            return self._get_job_result(job_uuid)

        return JobResult(exchangeObjects=[response] if response else [])

    # Delete is not supported for Gross Payments in HR Exchange API
