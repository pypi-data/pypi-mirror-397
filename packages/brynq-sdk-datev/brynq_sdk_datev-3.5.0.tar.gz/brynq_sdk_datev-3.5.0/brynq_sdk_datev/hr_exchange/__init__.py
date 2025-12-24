import base64
import os
from datetime import datetime
from typing import List, Optional, Literal

import requests
from brynq_sdk_brynq import BrynQ
# Import all resource classes
from .employees import Employees
from .absences import Absences
from .employment_periods import EmploymentPeriods
from .gross_payments import GrossPayments
from .hourly_wages import HourlyWages
from .monthly_records import MonthRecords
from .organization import Organization
import pandas as pd


class DatevHrExchange(BrynQ):
    def __init__(self, system_type: Optional[Literal['source', 'target']] = None, debug: bool = False, sandbox: bool = False):
        super().__init__()
        # Initialize with parent class
        self.debug = debug
        self.sandbox = sandbox
        self.timeout = 3600
        # Set base URL based on sandbox flag
        base_url = "https://hr-exchange.api.datev.de/platform"
        if sandbox:
            base_url += "-sandbox"
        self.base_url = f"{base_url}/v1"

        # Get credentials from BrynQ system
        credentials = self.interfaces.credentials.get(system="datev", system_type=system_type)
        credential_data = credentials.get('data')
        access_token = credential_data.get('access_token')
        self.app_client_id = os.environ.get('DATEV_CLIENT_ID')
        # Store client information
        self.client_id = f"{ os.environ.get('DATEV_CONSULTANT_NUMBER')}-{ os.environ.get('DATEV_CLIENT_NUMBER')}"

        # Set up headers for direct API calls (not via agent like lohn_und_gehalt)
        headers = {
            "Authorization": f"Bearer {access_token}",
            "X-Datev-Client-ID": self.app_client_id,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        self.session = requests.Session()
        self.session.headers.update(headers)

        if self.debug:
            print(f"Initialized HR Exchange with client_nr: {self.client_id}")
            print(f"Base URL: {self.base_url}")
            print(f"Sandbox mode: {sandbox}")

        # Initialize all resource classes
        self.employees = Employees(self)
        self.absences = Absences(self)
        self.employment_periods = EmploymentPeriods(self)
        self.gross_payments = GrossPayments(self)
        self.hourly_wages = HourlyWages(self)
        self.month_records = MonthRecords(self)
        self.organization = Organization(self)

        # Request tracking attributes
        self._total_requests = 0
        self._failed_requests = 0

        # HTTP logging attributes
        self._http_logs = []

    def _increment_request_count(self, failed: bool = False):
        """Increment the total request count and failed count if applicable.

        Args:
            failed: Whether this request failed
        """
        self._total_requests += 1
        if failed:
            self._failed_requests += 1

    def _get_request_failure_percentage(self) -> float:
        """Get the percentage of failed requests out of total requests.

        Returns:
            Percentage of failed requests (0.0 to 100.0)
        """
        if self._total_requests == 0:
            return 0.0
        return round((self._failed_requests / self._total_requests) * 100.0, 2)

    def get_request_stats(self) -> dict:
        """Get request statistics.

        Returns:
            Dictionary with total_requests, failed_requests, and failure_percentage
        """
        return {
            'total_requests': self._total_requests,
            'failed_requests': self._failed_requests,
            'failure_percentage': self._get_request_failure_percentage()
        }

    def _log_http_request(self, method: str, url: str, headers: dict, body: Optional[str] = None):
        """Log an HTTP request.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Full URL with query parameters
            headers: Request headers (authorization header will be excluded)
            body: Request body (optional)
        """
        # Filter out authorization header
        filtered_headers = {k: v for k, v in headers.items() if k.lower() != 'authorization'}

        log_entry = {
            'scope': 'HTTP-REQUEST',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'method': method,
            'url': url,
            'headers': filtered_headers,
            'body': body
        }

        self._http_logs.append(log_entry)

    def _log_http_response(self, status_code: int, status_message: str, headers: dict, body: Optional[str] = None):
        """Log an HTTP response.

        Args:
            status_code: HTTP status code
            status_message: HTTP status message
            headers: Response headers
            body: Response body (only for errors/status queries)
        """
        # Extract specific headers as requested
        response_headers = {}
        if 'X-Global-Transaction-ID' in headers:
            response_headers['X-Global-Transaction-ID'] = headers['X-Global-Transaction-ID']
        if 'V-Cap-Request-ID' in headers:
            response_headers['V-Cap-Request-ID'] = headers['V-Cap-Request-ID']

        log_entry = {
            'scope': 'HTTP-RESPONSE',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status_code': status_code,
            'status_message': status_message,
            'headers': response_headers,
            'body': body
        }

        self._http_logs.append(log_entry)

    def get_http_logs(self) -> pd.DataFrame:
        """Get all HTTP request/response logs.

        Returns:
            List of log entries with request and response data
        """
        return pd.DataFrame(self._http_logs.copy())
