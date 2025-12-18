"""
PaymentsOS API client library for session management and reporting.

This module provides a client interface to interact with the PaymentsOS API,
including session authentication, report request creation and retrieval, and
report file downloads with automatic decompression.

Classes
-------
PaymentsOSError
    Exception raised when PaymentsOS API returns a non-success response.
PaymentsOS
    Client for authenticating with and making requests to the PaymentsOS API.
"""

import logging
import shutil
import uuid
import gzip
import requests
from typing import Optional, Any
from datetime import datetime

# Creates a logger for this module
logger = logging.getLogger(__name__)


class PaymentsOSError(Exception):
    """
    Exception raised when PaymentsOS returns a non-success response.

    Parameters
    ----------
    status_code : int
        The HTTP status code returned by the PaymentsOS API.
    payload : Any
        The response payload or error message returned by PaymentsOS.

    Attributes
    ----------
    status_code : int
        The HTTP status code associated with the error.
    payload : Any
        The response payload or error message associated with the error.
    """

    def __init__(self, status_code: int, payload):
        """
        Initialize a PaymentsOS exception.

        Parameters
        ----------
        status_code : int
            The HTTP status code returned by the PaymentsOS API.
        payload : any
            The response payload from the PaymentsOS API containing error details.
        """
        super().__init__(f"PaymentsOS error {status_code}: {payload}")
        self.status_code = status_code
        self.payload = payload


class PaymentsOS:
    """
    Client for interacting with the PaymentsOS API, including session management and reporting.

    This class provides methods to authenticate with PaymentsOS, manage session tokens,
    create and retrieve report requests, and download report files.

    Parameters
    ----------
    email : str
        The login email to authenticate the session.
    password : str
        The login password to authenticate the session.
    account_id : str
        Default account id to use for account-scoped endpoints (e.g., Reporting).
    api_version : str, optional
        API version header (default is "1.1.0").
    environment : str, optional
        'test' or 'live'. Used by downstream APIs (default is "test").
    timeout : int, optional
        Request timeout in seconds (default is 30).

    Attributes
    ----------
    token : Optional[str]
        The current session token (read-only).
    _base_url : str
        Base URL for PaymentsOS API.
    _api_version : str
        API version used in requests.
    _environment : str
        Environment ("test" or "live").
    _timeout : int
        Default request timeout in seconds.
    _account_id : str
        Default account ID for account-scoped endpoints.
    _email : str
        Login email (private).
    _password : str
        Login password (private).
    __token : Optional[str]
        Session token (private).

    Methods
    -------
    create_session()
        Authenticate and obtain a session token.
    create_report_request(...)
        Create a report request in PaymentsOS.
    retrieve_report_request(report_request_id, timeout=None)
        Retrieve a report request by its ID.
    download_report_to_csv(report_url, output_path)
        Download and decompress a report file to CSV.
    """

    def __init__(
        self,
        email: str,
        password: str,
        account_id: str,
        api_version: str = "1.1.0",
        environment: str = "test",  # or "live"
        timeout: int = 30,
        custom_logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize the PaymentOS client and authenticate to obtain a session token.

        Parameters
        ----------
        email : str
            The login email to authenticate the session.
        password : str
            The login password to authenticate the session.
        account_id : str
            Default account id to use for account-scoped endpoints (e.g., Reporting).
        api_version : str, optional
            API version header (default is "1.1.0").
        environment : str, optional
            'test' or 'live'. Used by downstream APIs (default is "test").
        timeout : int, optional
            Request timeout in seconds (default is 30).
        custom_logger : logging.Logger, optional
            Provide a custom logger instance. If None, use the default logger.

        Notes
        -----
        This constructor authenticates immediately and stores the session token for use in subsequent API calls.
        """
        # Init logging
        # Use provided logger or create a default one
        self._logger = custom_logger or logging.getLogger(name=__name__)

        # Init variables
        self._base_url = "https://api.paymentsos.com"
        self._api_version = api_version
        self._environment = environment
        self._timeout = timeout
        self._account_id = account_id

        # Credentials (never print in logs)
        self._email = email
        self._password = password

        self.__token: Optional[str] = None

        # Authenticate immediately
        self.create_session()

    @property
    def token(self) -> Optional[str]:
        """
        Return the current session token.

        Returns
        -------
        Optional[str]
            The current session token if authenticated, otherwise None.
        """
        return self.__token

    def _bearer_headers(self, *, idempotency: bool = False) -> dict[str, str]:
        """
        Build headers for Bearer-authenticated API calls.

        Parameters
        ----------
        idempotency : bool, optional
            Whether to include an idempotency key in the headers (default is False).

        Returns
        -------
        dict of str to str
            Dictionary of HTTP headers for Bearer-authenticated requests.

        Raises
        ------
        PaymentsOSError
            If the session token is missing (i.e., not authenticated).
        """
        if not self.__token:
            raise PaymentsOSError(
                401, "Missing session token; call create_session() first."
            )

        # Headers
        headers = {
            "Authorization": f"Bearer {self.__token}",
            "Content-Type": "application/json",
            "api-version": self._api_version,
            "x-payments-os-env": self._environment,
        }

        # Add idempotency key if requested
        if idempotency:
            headers["idempotency-key"] = str(uuid.uuid4())

        return headers

    def create_session(self) -> None:
        """
        Create a PaymentsOS Management session and store the session token.

        This method authenticates with the PaymentsOS API using the configured email and password,
        and stores the resulting session token for use in subsequent API calls.

        Raises
        ------
        RuntimeError
            If the API response status code is not 201 (Created), indicating authentication failure.

        Notes
        -----
        The session token is stored internally and used for Bearer-authenticated requests.
        """
        self._logger.info(msg="Creating PaymentsOS session")

        # Headers
        headers = {
            "Content-Type": "application/json",
            "api-version": self._api_version,  # recommended to include
            "idempotency-key": str(uuid.uuid4()),
        }

        # Endpoint
        url = f"{self._base_url.rstrip('/')}/sessions"

        # Payload built from provided credentials
        payload = {
            "email": self._email,
            "password": self._password,
        }

        # Make the request
        resp = requests.post(url, json=payload, headers=headers, timeout=self._timeout)

        if resp.status_code != 201:
            raise RuntimeError(f"{resp.status_code}, {resp.content}")

        self.__token = resp.json().get("session_token")

    def create_report_request(
        self,
        report_template_id: str,
        date_from: datetime,
        date_to: datetime,
        report_name: str,
        filter_timezone: str,
        timezone: str,
        # IANA TZ for display; defaults to filter_timezone
        display_timezone: Optional[str] = None,
        include_sftp_report_name_prefix: bool = False,
        idempotency_key: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> dict[str, Any]:
        """
        Create a PaymentsOS 'Report Request' using the Reporting API.

        This method builds and submits a report request payload to PaymentsOS, specifying the report template,
        date range, timezones, and other options. Returns the JSON response from the API.

        Parameters
        ----------
        report_template_id : str
            The ID of the report template to use.
        date_from : datetime
            Start timestamp (ISO-8601), e.g. "2025-08-01T00:00:00Z".
        date_to : datetime
            End timestamp (ISO-8601), e.g. "2025-12-01T00:00:00Z".
        report_name : str
            Human-friendly name for this report request.
        filter_timezone : str
            IANA timezone name used for filtering (e.g., "America/Bogota").
        timezone : str
            Offset string (e.g., "-05:00").
        display_timezone : str, optional
            IANA timezone for how timestamps are displayed in the report. Defaults to filter_timezone.
        include_sftp_report_name_prefix : bool, optional
            Whether to prefix the generated file name when delivered to SFTP.
        account_id : str, optional
            Target account ID; defaults to the client's configured account_id.
        idempotency_key : str, optional
            Unique key for safe retries. If omitted, a UUID will be generated.
        timeout : int, optional
            Per-request timeout override in seconds.

        Returns
        -------
        dict
            JSON response returned by PaymentsOS for the created report request.

        Raises
        ------
        RuntimeError
            If the API response status code is not 2xx.
        """
        self._logger.info(msg="Creating PaymentsOS report request")

        # Headers
        # Authorization, Content-Type, api-version, x-payments-os-env
        headers = self._bearer_headers()
        headers["idempotency-key"] = idempotency_key or str(uuid.uuid4())

        # Payload
        str_date_from = date_from.strftime("%Y-%m-%dT%H:%M:%SZ")
        str_date_to = date_to.strftime("%Y-%m-%dT%H:%M:%SZ")

        # Build the payload from arguments
        payload: dict[str, Any] = {
            "date_range": {
                "date_from": str_date_from,
                "date_to": str_date_to,
            },
            "filter_timezone": filter_timezone,
            "report_name": report_name,
            "include_sftp_report_name_prefix": include_sftp_report_name_prefix,
            "report_template_id": report_template_id,
            "display_timezone": display_timezone or filter_timezone,
            "timezone": timezone,
        }

        # Endpoint
        url = f'{self._base_url.rstrip("/")}/accounts/{self._account_id}/reports'

        # Make the request
        resp = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=timeout or self._timeout,
        )

        if resp.status_code // 100 != 2:
            raise RuntimeError(f"{resp.status_code}, {resp.content}")

        return resp.json()

    def retrieve_report_request(
        self,
        report_request_id: str,
        timeout: Optional[int] = None,
    ) -> requests.Response:
        """
        Retrieve a PaymentsOS Report Request by its ID.

        This method sends a GET request to the PaymentsOS Reporting API to fetch the details
        of a specific report request. Returns the raw `requests.Response` object for further
        processing by the caller.

        Parameters
        ----------
        report_request_id : str
            The unique identifier of the report request to retrieve.
        timeout : int, optional
            Timeout in seconds for the request. If not provided, uses the client's default timeout.

        Returns
        -------
        requests.Response
            The raw HTTP response object returned by the PaymentsOS API.

        Notes
        -----
        The caller is responsible for handling response status and parsing the response content.

        Raises
        ------
        requests.RequestException
            If an error occurs during the HTTP request.

        Docs
        ------
        https://developers.paymentsos.com/docs/apis/reporting/1.1.0/#tag/Reports/operation/retrieve-a-report-request
        """
        self._logger.info(
            msg=f"Retrieving PaymentsOS report request {report_request_id}"
        )

        # Headers
        # Bearer headers include: Authorization, Content-Type, api-version, x-payments-os-env
        headers = self._bearer_headers()  # no idempotency needed for GET

        # Endpoint: account-scoped path with report_request_id
        url = f'{self._base_url.rstrip("/")}/accounts/{self._account_id}/reports/{report_request_id}'

        # Send request
        # Return raw response; caller handles raise_for_status / parsing
        resp = requests.get(url, headers=headers, timeout=timeout or self._timeout)

        return resp

    def download_report_to_csv(self, report_url: str, output_path: str):
        """
        Download a gzip-compressed report from a URL and save the decompressed content as a CSV file.

        This method performs an HTTP GET request to the specified `report_url` using a streaming response.
        The response body is treated as a gzip stream, which is transparently decompressed and written
        to the specified `output_path` as a CSV file.

        Parameters
        ----------
        report_url : str
            The URL pointing to the gzip-compressed report file.
        output_path : str
            The local file path where the decompressed CSV will be saved.

        Raises
        ------
        requests.HTTPError
            If the HTTP request to download the report fails.
        OSError
            If there is an error writing the decompressed file to disk.

        Notes
        -----
        The output file is overwritten if it already exists.
        """
        self._logger.info(
            msg=f"Downloading and decompressing report from {report_url} to {output_path}"
        )

        # Send request to download the file
        response = requests.get(report_url, stream=True)
        response.raise_for_status()

        # Decompress gzip -> write to CSV
        with open(file=output_path, mode="wb") as f:
            response.raw.decode_content = True

            with gzip.GzipFile(fileobj=response.raw, mode="rb") as gz:
                shutil.copyfileobj(gz, f)


# eof
