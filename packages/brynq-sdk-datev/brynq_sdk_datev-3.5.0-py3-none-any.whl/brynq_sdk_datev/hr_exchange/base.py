import json
import time
import requests
from typing import Dict, Any, Optional, Union, List, Type
import pandas as pd
from datetime import datetime
from pydantic import BaseModel
from uuid import UUID
from .schemas._api import Job, JobResult


class BaseHrExchangeResource:
    """Base class for all HR Exchange resources with job handling capabilities"""

    def __init__(self, datev):
        from . import DatevHrExchange
        self.datev: DatevHrExchange = datev
        self.debug = datev.debug

    def _make_request(
        self,
        endpoint_path: str,
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None,
        timeout: Optional[int] = None,
        target_system: Optional[str] = None,
        notify_url: Optional[str] = None,
        notify_auth: Optional[str] = None
    ) -> Any:
        """
        Make a direct request to the HR Exchange API

        Args:
            endpoint_path: The endpoint path to call (relative to base_url)
            method: HTTP method (GET, POST, PUT, DELETE)
            params: Query parameters
            json_data: JSON body for POST/PUT requests
            timeout: Request timeout (defaults to instance timeout)
            target_system: Target payroll system ('lug' or 'lodas')
            notify_url: URL to notify when job status changes
            notify_auth: Authorization header for notifications

        Returns:
            API response data
        """
        url = f"{self.datev.base_url}/{endpoint_path}"
        timeout = timeout or self.datev.timeout

        # Build headers with optional additions
        headers = self.datev.session.headers.copy()
        if target_system:
            headers["Target-System"] = target_system
        if notify_url:
            headers["Notify-Url"] = notify_url
        if notify_auth:
            headers["Notify-Auth"] = notify_auth

        # Build full URL with query parameters for logging
        full_url = url
        if params:
            from urllib.parse import urlencode
            full_url += f"?{urlencode(params)}"

        # Prepare request body for logging
        request_body = None
        if json_data is not None:
            request_body = json.dumps(json_data, default=str)

        # Log the HTTP request
        self.datev._log_http_request(method, full_url, headers, request_body)

        if self.debug:
            print(f"Making {method} request to {url}")
            if params:
                print(f"Query params: {params}")
            if json_data:
                print(f"Request body: {json.dumps(json_data, indent=2, default=str)}")
            print(f"Headers: {headers}")

        try:
            resp = self.datev.session.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json_data,
                timeout=timeout
            )

            if self.debug:
                print(f"Response status: {resp.status_code}")
                try:
                    print(f"Response body: {json.dumps(resp.json(), indent=2)}")
                except:
                    print(f"Response body could not be parsed as JSON: {resp.text[:200]}...")

            resp.raise_for_status()

            # Track successful request
            self.datev._increment_request_count(failed=False)

            # Log successful response (without body for data protection)
            response_body = None
            # Only log response body for status queries or if explicitly requested
            if resp.status_code in [200, 201, 202] and method != "GET":
                try:
                    response_body = resp.text
                except:
                    response_body = None

            self.datev._log_http_response(resp.status_code, resp.reason, dict(resp.headers), response_body)

            # Return parsed JSON or empty dict for 204 No Content
            if resp.status_code == 204:
                return {}
            return resp.json()
        except Exception as e:
            # Log error response if we have response details
            if 'resp' in locals():
                # For error responses, include the body as it's an error message
                error_body = None
                try:
                    error_body = resp.text
                except:
                    error_body = str(e)

                self.datev._log_http_response(resp.status_code, resp.reason, dict(resp.headers), error_body)

            # Track failed request
            self.datev._increment_request_count(failed=True)
            raise e

    def _create_job(
        self,
        resource_name: str,
        resource_id: Optional[str] = None,
        reference_date: Optional[str] = None,
        sub_resource: Optional[Dict[str, Any]] = None,
        target_system: Optional[str] = None,
        notify_url: Optional[str] = None,
        notify_authorization_header: Optional[str] = None
    ) -> str:
        """
        Create a new job and return the job UUID

        Args:
            resource_name: Name of the resource to fetch (e.g., 'employees', 'absences')
            resource_id: Optional specific resource ID
            reference_date: Reference date in YYYY-MM format
            sub_resource: Optional sub-resource specification
            target_system: Target payroll system ('lug' or 'lodas')
            notify_url: Optional URL to notify when job completes
            notify_authorization_header: Optional authorization header for notifications

        Returns:
            Job UUID as string
        """
        endpoint = f"clients/{self.datev.client_id}/jobs"

        # Build payload according to API specification
        payload = {
            "resource_name": resource_name
        }

        if resource_id:
            payload["id"] = resource_id

        if reference_date:
            payload["reference_date"] = reference_date

        if sub_resource:
            payload["sub_resource"] = sub_resource

        if self.debug:
            print(f"Creating job with data: {payload}")

        response = self._make_request(
            endpoint,
            method="POST",
            json_data=payload,
            target_system=target_system,
            notify_url=notify_url,
            notify_auth=notify_authorization_header
        )

        # Extract job UUID from response
        if isinstance(response, dict) and "id" in response:
            job_uuid = str(response["id"])
        else:
            raise ValueError("Job creation response did not contain job ID")

        if self.debug:
            print(f"Created job with UUID: {job_uuid}")

        return job_uuid

    def _wait_for_job(
        self,
        job_uuid: str,
        max_wait_time: int = 900,
        poll_interval: int = 60
    ) -> Job:
        """
        Wait for a job to complete

        Args:
            job_uuid: The job UUID to monitor
            max_wait_time: Maximum time to wait in seconds
            poll_interval: How often to check job status in seconds

        Returns:
            Completed Job object

        Raises:
            TimeoutError: If job doesn't complete within max_wait_time
            ValueError: If job fails
        """
        start_time = time.time()
        endpoint = f"clients/{self.datev.client_id}/jobs/{job_uuid}"

        while time.time() - start_time < max_wait_time:
            if self.debug:
                print(f"Checking job status: {job_uuid}")

            response = self._make_request(endpoint)
            job = Job(**response)

            if self.debug:
                print(f"Job state: {job.state}")

            if job.state == "SUCCESSFUL":
                return job
            elif job.state == "failed":
                error_msg = "Job failed"
                if job.errors:
                    error_details = [f"{err.error}: {err.error_description}" for err in job.errors]
                    error_msg += f": {'; '.join(error_details)}"
                raise ValueError(error_msg)
            elif job.state in ["cancelled", "expired"]:
                raise ValueError(f"Job was {job.state}")

            time.sleep(poll_interval)

        raise TimeoutError(f"Job {job_uuid} did not complete within {max_wait_time} seconds")

    def _get_job_result(self, job_uuid: str) -> JobResult:
        """
        Get the result of a completed job

        Args:
            job_uuid: The job UUID

        Returns:
            JobResult object
        """
        endpoint = f"clients/{self.datev.client_id}/jobs/{job_uuid}/result"

        if self.debug:
            print(f"Getting job result: {job_uuid}")

        # Log the HTTP request
        request_url = f"{self.datev.base_url}/{endpoint}"
        request_headers = self.datev.session.headers.copy()
        self.datev._log_http_request("GET", request_url, request_headers)

        try:
            # The API returns 301 redirects, make sure we follow them
            response = self.datev.session.request(
                method="GET",
                url=f"{self.datev.base_url}/{endpoint}",
                timeout=self.datev.timeout,
                allow_redirects=True  # Explicitly follow redirects to go to the URL specified byt resource type
            )

            if self.debug:
                print(f"Final URL after redirects: {response.url}")
                print(f"Response status: {response.status_code}")
                try:
                    print(f"Response body: {response.json()}")
                except:
                    print(f"Response body could not be parsed as JSON: {response.text[:200]}...")

            response.raise_for_status()

             # Track successful request
            self.datev._increment_request_count(failed=False)

            # Log successful response (do not include body for job results as they contain actual data)
            self.datev._log_http_response(response.status_code, response.reason, dict(response.headers), None)

            # Return parsed JSON or empty dict for 204 No Content
            if response.status_code == 204:
                return JobResult()
            return JobResult(**response.json())
        except Exception as e:
            # Log error response if we have response details
            if 'response' in locals():
                # For error responses, include the body as it's an error message
                error_body = None
                try:
                    error_body = response.text
                except:
                    error_body = str(e)

                self.datev._log_http_response(response.status_code, response.reason, dict(response.headers), error_body)

            # Track failed request
            self.datev._increment_request_count(failed=True)
            raise e

    def _create_and_wait_for_job(
        self,
        resource_name: str,
        resource_id: Optional[str] = None,
        reference_date: Optional[str] = None,
        sub_resource: Optional[Dict[str, Any]] = None,
        target_system: Optional[str] = None,
        max_wait_time: int = 900,
        poll_interval: int = 60,
        notify_url: Optional[str] = None,
        notify_authorization_header: Optional[str] = None
    ) -> JobResult:
        """
        Create a job, wait for completion, and return the result

        Args:
            resource_name: Name of the resource to fetch
            resource_id: Optional specific resource ID
            reference_date: Reference date in YYYY-MM format
            sub_resource: Optional sub-resource specification
            target_system: Target payroll system ('lug' or 'lodas')
            max_wait_time: Maximum time to wait in seconds
            poll_interval: How often to check job status in seconds
            notify_url: Optional URL to notify when job completes
            notify_authorization_header: Optional authorization header for notifications

        Returns:
            JobResult object
        """
        job_uuid = self._create_job(
            resource_name=resource_name,
            resource_id=resource_id,
            reference_date=reference_date,
            sub_resource=sub_resource,
            target_system=target_system,
            notify_url=notify_url,
            notify_authorization_header=notify_authorization_header
        )
        self._wait_for_job(job_uuid, max_wait_time, poll_interval)
        return self._get_job_result(job_uuid)

    def _validate_request_data(
        self,
        data: Dict[str, Any],
        schema_class: Type[BaseModel]
    ) -> Dict[str, Any]:
        """
        Validate request data against a pydantic schema and format dates

        Args:
            data: The data to validate
            schema_class: The pydantic schema class to use for validation

        Returns:
            Validated and formatted data dictionary
        """
        try:
            # Validate against schema
            validated = schema_class(**data)
            validated_data = validated.model_dump(exclude_none=True)

            # Show what fields were dropped if in debug mode
            if self.debug:
                dropped_fields = {k: v for k, v in data.items() if k not in validated_data}
                if dropped_fields:
                    print(f"Dropped fields: {dropped_fields}")

            # Format dates automatically
            validated_data = self._format_date_fields(validated_data)

            # Show final data if in debug mode
            if self.debug:
                print(f"Validated data: {validated_data}")

            return validated_data

        except Exception as e:
            if self.debug:
                print(f"Validation error: {str(e)}")
            raise ValueError(f"Invalid data: {str(e)}")

    def _format_date_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Automatically format datetime objects based on field name:
        - reference_date fields: YYYY-MM format (year-month)
        - Other date fields: YYYY-MM-DD format (full date)

        Args:
            data: The data dictionary

        Returns:
            Data dictionary with formatted date fields
        """
        formatted_data = {}

        for key, value in data.items():
            if isinstance(value, datetime):
                # Format reference_date as YYYY-MM, others as YYYY-MM-DD
                if "reference_date" in key.lower():
                    formatted_data[key] = value.strftime("%Y-%m")
                else:
                    formatted_data[key] = value.strftime("%Y-%m-%d")
            elif isinstance(value, dict):
                # Handle nested dictionaries
                formatted_data[key] = self._format_date_fields(value)
            elif isinstance(value, list):
                # Handle lists of items
                formatted_data[key] = [
                    self._format_date_fields(item) if isinstance(item, dict)
                    else (
                        item.strftime("%Y-%m") if isinstance(item, datetime) and "reference" in str(item)
                        else (item.strftime("%Y-%m-%d") if isinstance(item, datetime) else item)
                    )
                    for item in value
                ]
            else:
                formatted_data[key] = value

        return formatted_data
