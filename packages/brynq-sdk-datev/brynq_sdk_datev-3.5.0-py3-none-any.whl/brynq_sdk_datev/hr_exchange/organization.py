from datetime import datetime
from typing import Dict, Any, Optional, Tuple, NamedTuple
import pandas as pd
from .base import BaseHrExchangeResource
from .schemas.organizational import (
    ClientGet, SalaryTypeGet, DepartmentGet, CostCenterGet,
    HealthInsurerGet, BusinessUnitGet
)
from .schemas._api import JobResult
from brynq_sdk_functions import Functions


class ClientDataResult(NamedTuple):
    """Result structure for client data with separate DataFrames for each component"""
    client: Tuple[pd.DataFrame, pd.DataFrame]  # (valid, invalid)
    salary_types: Tuple[pd.DataFrame, pd.DataFrame]
    departments: Tuple[pd.DataFrame, pd.DataFrame]
    cost_centers: Tuple[pd.DataFrame, pd.DataFrame]
    health_insurers: Tuple[pd.DataFrame, pd.DataFrame]
    business_units: Tuple[pd.DataFrame, pd.DataFrame]


class Organization(BaseHrExchangeResource):
    """
    Client Data resource for DATEV HR Exchange
    Handles client data operations via jobs
    """

    def __init__(self, datev):
        super().__init__(datev)

    def get(
        self,
        reference_date: Optional[datetime] = None
    ) -> ClientDataResult:
        """
        Get client data via job-based processing and split into separate validated components

        Args:
            reference_date: Optional reference date
            max_wait_time: Maximum time to wait for job completion
            poll_interval: How often to check job status

        Returns:
            ClientDataResult with separate DataFrames for each component
        """
        reference_date = reference_date or datetime.now()
        reference_date_str = reference_date.strftime("%Y-%m")

        if self.debug:
            print(f"Creating job to fetch client data for date: {reference_date_str}")

        # Create job and wait for result
        job_result = self._create_and_wait_for_job(
            resource_name="client-data",
            reference_date=reference_date_str
        )

        # Extract client data from job result
        raw_client_data = []
        if job_result.exchangeObjects:
            raw_client_data = job_result.exchangeObjects

        if not raw_client_data:
            # Return empty DataFrames if no data
            empty_df = pd.DataFrame()
            return ClientDataResult(
                client=(empty_df, empty_df),
                salary_types=(empty_df, empty_df),
                departments=(empty_df, empty_df),
                cost_centers=(empty_df, empty_df),
                health_insurers=(empty_df, empty_df),
                business_units=(empty_df, empty_df)
            )

        # Extract and validate core client data (excluding list fields)
        client_core = []
        for client in raw_client_data:
            core_data = {k: v for k, v in client.items()
                        if k not in ['salary_types', 'departments', 'cost_centers',
                                   'health_insurers', 'business_units']}
            client_core.append(core_data)

        client_df = pd.json_normalize(client_core)
        client_valid, client_invalid = Functions.validate_data(client_df, ClientGet, debug=self.debug)

                # Extract and validate each list component
        def extract_and_validate(list_field: str, schema_class):
            all_items = []
            for client in raw_client_data:
                items = client.get(list_field, [])
                client_name = client.get('name', 'Unknown')  # Get client identifier
                if items:
                    # Add client_name to each item to maintain relationship
                    for item in items:
                        item_with_client = item.copy()
                        item_with_client['client_name'] = client_name
                        all_items.append(item_with_client)

            if all_items:
                df = pd.json_normalize(all_items)
                return Functions.validate_data(df, schema_class, debug=self.debug)
            else:
                empty_df = pd.DataFrame()
                return empty_df, empty_df

        salary_types_valid, salary_types_invalid = extract_and_validate('salary_types', SalaryTypeGet)
        departments_valid, departments_invalid = extract_and_validate('departments', DepartmentGet)
        cost_centers_valid, cost_centers_invalid = extract_and_validate('cost_centers', CostCenterGet)
        health_insurers_valid, health_insurers_invalid = extract_and_validate('health_insurers', HealthInsurerGet)
        business_units_valid, business_units_invalid = extract_and_validate('business_units', BusinessUnitGet)

        return ClientDataResult(
            client=(client_valid, client_invalid),
            salary_types=(salary_types_valid, salary_types_invalid),
            departments=(departments_valid, departments_invalid),
            cost_centers=(cost_centers_valid, cost_centers_invalid),
            health_insurers=(health_insurers_valid, health_insurers_invalid),
            business_units=(business_units_valid, business_units_invalid)
        )
