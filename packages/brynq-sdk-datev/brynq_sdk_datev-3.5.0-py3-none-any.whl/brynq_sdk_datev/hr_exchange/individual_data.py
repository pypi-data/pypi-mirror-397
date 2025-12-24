from datetime import datetime
from typing import Optional, Tuple
import pandas as pd
from .base import BaseHrExchangeResource
from .schemas._api import JobResult
from .schemas.individual_data import IndividualDataGet
from brynq_sdk_functions import Functions


class IndividualDataResource(BaseHrExchangeResource):
    """
    Individual Data resource for DATEV HR Exchange
    """

    def __init__(self, datev):
        super().__init__(datev)

    def get(
        self,
        personnel_number: Optional[int] = None,
        reference_date: Optional[datetime] = None
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get individual data via job processing

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
            print(f"Creating job to fetch individual data for date: {reference_date_str}")

        # Create job and wait for result using similar structure as employees
        job_result = self._create_and_wait_for_job(
            resource_name="individual-data",
            resource_id=str(personnel_number) if personnel_number else None,
            reference_date=reference_date_str
        )

        # Extract data from job result
        data = []
        if job_result.exchangeObjects:
            data = job_result.exchangeObjects

        # Normalize and inject employee_id if present at parent level
        rows = []
        for obj in data:
            row = obj.get('individual_data') if 'individual_data' in obj else obj
            employee_id = obj.get('employee_id') or obj.get('id')
            if row is not None:
                flat = dict(row)
                flat['employee_id'] = employee_id
                rows.append(flat)

        df = pd.json_normalize(rows) if rows else pd.DataFrame()
        valid_data, invalid_data = Functions.validate_data(df, IndividualDataGet, debug=self.debug)

        return valid_data, invalid_data
