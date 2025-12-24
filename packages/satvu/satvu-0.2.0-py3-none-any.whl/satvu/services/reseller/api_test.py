"""
Tests for reseller service.

Generated from OpenAPI spec version 0.1.0.
Uses property-based testing with hypothesis-jsonschema.
"""

from unittest.mock import Mock

import pook
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis_jsonschema import from_schema
from pydantic import TypeAdapter

from satvu import SatVuSDK, create_http_client
from satvu.http.errors import ClientError
from satvu.services.reseller.models.create_user import CreateUser
from satvu.services.reseller.models.get_companies import GetCompanies
from satvu.services.reseller.models.get_users import GetUsers
from satvu.services.reseller.models.search_companies import SearchCompanies
from satvu.services.reseller.models.search_users import SearchUsers

from .test_schemas import (
    get_request_body_schema,
    get_response_schema,
)


@pytest.mark.parametrize("backend", ["stdlib", "httpx", "urllib3", "requests"])
class TestResellerService:
    """Property-based tests for ResellerService."""

    @pytest.fixture(autouse=True)
    def setup(self, backend):
        """Set up test fixtures before each test method."""
        # Mock the auth token
        mock_get_token = Mock(return_value="test_token")

        # Construct base URL for the reseller service
        # We need to match how SDKClient builds its base_url in __init__
        subdomain = "api"
        env_part = "qa."
        base_path = "/resellers/v1"
        self.base_url = f"https://{subdomain}.{env_part}satellitevu.com{base_path}"

        # Create HTTP client with specified backend
        http_client = create_http_client(
            backend=backend,
            base_url=self.base_url,
            get_token=mock_get_token,
        )

        self.sdk = SatVuSDK(
            client_id="test_client_id",
            client_secret="test_client_secret",  # pragma: allowlist secret
            http_client=http_client,
            env="qa",
        )

        # Override the token getter with our mock
        self.sdk.reseller._get_token = mock_get_token

    @settings(
        max_examples=10,
        deadline=None,
        suppress_health_check=[
            HealthCheck.filter_too_much,
            HealthCheck.too_slow,
            HealthCheck.data_too_large,
        ],
    )
    @given(
        response_data=from_schema(get_response_schema("/user", "post", "201")),
        body_data=from_schema(get_request_body_schema("/user", "post")),
    )
    def test_create_users_201(
        self,
        backend,
        response_data,
        body_data,
    ):
        """
        Test create_users with 201 response.
        """
        # Generate path parameters
        path = "/user"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP response
        pook.post(url).reply(201).json(response_data).header(
            "Content-Type", "application/json"
        )

        # Call the service method
        # For list types, use TypeAdapter to validate
        body_adapter = TypeAdapter(list[CreateUser])
        body = body_adapter.validate_python(body_data)

        result = self.sdk.reseller.create_users(
            items=body,
        )

        # Assert response parses correctly
        assert result is not None

        # Assert response type matches expected type
        assert isinstance(result, list)

    @settings(
        max_examples=10,
        deadline=None,
        suppress_health_check=[
            HealthCheck.filter_too_much,
            HealthCheck.too_slow,
            HealthCheck.data_too_large,
        ],
    )
    @given(
        response_data=from_schema(get_response_schema("/user", "post", "422")),
        body_data=from_schema(get_request_body_schema("/user", "post")),
    )
    def test_create_users_422_error(
        self,
        backend,
        response_data,
        body_data,
    ):
        """
        Test create_users with 422 error response.

        HTTP 422 errors raise ClientError.
        """
        # Generate path parameters
        path = "/user"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP error response
        pook.post(url).reply(422).json(response_data).header(
            "Content-Type", "application/json"
        )

        # For list types, use TypeAdapter to validate
        body_adapter = TypeAdapter(list[CreateUser])
        body = body_adapter.validate_python(body_data)

        # HTTP 422 should raise ClientError
        with pytest.raises(ClientError) as exc_info:
            self.sdk.reseller.create_users(
                items=body,
            )

        # Verify the exception contains the correct status code
        assert exc_info.value.status_code == 422

    @settings(
        max_examples=10,
        deadline=None,
        suppress_health_check=[
            HealthCheck.filter_too_much,
            HealthCheck.too_slow,
            HealthCheck.data_too_large,
        ],
    )
    @given(
        response_data=from_schema(get_response_schema("/users", "get", "200")),
    )
    def test_get_users_200(
        self,
        backend,
        response_data,
    ):
        """
        Test get_users with 200 response.
        """
        # Generate path parameters
        path = "/users"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP response
        pook.get(url).reply(200).json(response_data).header(
            "Content-Type", "application/json"
        )

        # Call the service method

        result = self.sdk.reseller.get_users()

        # Assert response parses correctly
        assert result is not None

        # Assert response type matches expected type
        assert isinstance(result, GetUsers)

    @settings(
        max_examples=10,
        deadline=None,
        suppress_health_check=[
            HealthCheck.filter_too_much,
            HealthCheck.too_slow,
            HealthCheck.data_too_large,
        ],
    )
    @given(
        response_data=from_schema(get_response_schema("/users", "get", "422")),
    )
    def test_get_users_422_error(
        self,
        backend,
        response_data,
    ):
        """
        Test get_users with 422 error response.

        HTTP 422 errors raise ClientError.
        """
        # Generate path parameters
        path = "/users"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP error response
        pook.get(url).reply(422).json(response_data).header(
            "Content-Type", "application/json"
        )

        # HTTP 422 should raise ClientError
        with pytest.raises(ClientError) as exc_info:
            self.sdk.reseller.get_users()

        # Verify the exception contains the correct status code
        assert exc_info.value.status_code == 422

    @settings(
        max_examples=10,
        deadline=None,
        suppress_health_check=[
            HealthCheck.filter_too_much,
            HealthCheck.too_slow,
            HealthCheck.data_too_large,
        ],
    )
    @given(
        response_data=from_schema(get_response_schema("/companies", "get", "200")),
    )
    def test_get_companies_200(
        self,
        backend,
        response_data,
    ):
        """
        Test get_companies with 200 response.
        """
        # Generate path parameters
        path = "/companies"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP response
        pook.get(url).reply(200).json(response_data).header(
            "Content-Type", "application/json"
        )

        # Call the service method

        result = self.sdk.reseller.get_companies()

        # Assert response parses correctly
        assert result is not None

        # Assert response type matches expected type
        assert isinstance(result, GetCompanies)

    @settings(
        max_examples=10,
        deadline=None,
        suppress_health_check=[
            HealthCheck.filter_too_much,
            HealthCheck.too_slow,
            HealthCheck.data_too_large,
        ],
    )
    @given(
        response_data=from_schema(get_response_schema("/companies", "get", "422")),
    )
    def test_get_companies_422_error(
        self,
        backend,
        response_data,
    ):
        """
        Test get_companies with 422 error response.

        HTTP 422 errors raise ClientError.
        """
        # Generate path parameters
        path = "/companies"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP error response
        pook.get(url).reply(422).json(response_data).header(
            "Content-Type", "application/json"
        )

        # HTTP 422 should raise ClientError
        with pytest.raises(ClientError) as exc_info:
            self.sdk.reseller.get_companies()

        # Verify the exception contains the correct status code
        assert exc_info.value.status_code == 422

    @settings(
        max_examples=10,
        deadline=None,
        suppress_health_check=[
            HealthCheck.filter_too_much,
            HealthCheck.too_slow,
            HealthCheck.data_too_large,
        ],
    )
    @given(
        response_data=from_schema(get_response_schema("/search/users", "post", "200")),
        body_data=from_schema(get_request_body_schema("/search/users", "post")),
    )
    def test_search_users_200(
        self,
        backend,
        response_data,
        body_data,
    ):
        """
        Test search_users with 200 response.
        """
        # Generate path parameters
        path = "/search/users"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP response
        pook.post(url).reply(200).json(response_data).header(
            "Content-Type", "application/json"
        )

        # Call the service method
        # Parse body_data into Pydantic model
        body = SearchUsers.model_validate(body_data)

        result = self.sdk.reseller.search_users(
            body=body,
        )

        # Assert response parses correctly
        assert result is not None

        # Assert response type matches expected type
        assert isinstance(result, GetUsers)

    @settings(
        max_examples=10,
        deadline=None,
        suppress_health_check=[
            HealthCheck.filter_too_much,
            HealthCheck.too_slow,
            HealthCheck.data_too_large,
        ],
    )
    @given(
        response_data=from_schema(get_response_schema("/search/users", "post", "422")),
        body_data=from_schema(get_request_body_schema("/search/users", "post")),
    )
    def test_search_users_422_error(
        self,
        backend,
        response_data,
        body_data,
    ):
        """
        Test search_users with 422 error response.

        HTTP 422 errors raise ClientError.
        """
        # Generate path parameters
        path = "/search/users"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP error response
        pook.post(url).reply(422).json(response_data).header(
            "Content-Type", "application/json"
        )

        # Parse body_data into Pydantic model
        body = SearchUsers.model_validate(body_data)

        # HTTP 422 should raise ClientError
        with pytest.raises(ClientError) as exc_info:
            self.sdk.reseller.search_users(
                body=body,
            )

        # Verify the exception contains the correct status code
        assert exc_info.value.status_code == 422

    @settings(
        max_examples=10,
        deadline=None,
        suppress_health_check=[
            HealthCheck.filter_too_much,
            HealthCheck.too_slow,
            HealthCheck.data_too_large,
        ],
    )
    @given(
        response_data=from_schema(
            get_response_schema("/search/companies", "post", "200")
        ),
        body_data=from_schema(get_request_body_schema("/search/companies", "post")),
    )
    def test_search_companies_200(
        self,
        backend,
        response_data,
        body_data,
    ):
        """
        Test search_companies with 200 response.
        """
        # Generate path parameters
        path = "/search/companies"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP response
        pook.post(url).reply(200).json(response_data).header(
            "Content-Type", "application/json"
        )

        # Call the service method
        # Parse body_data into Pydantic model
        body = SearchCompanies.model_validate(body_data)

        result = self.sdk.reseller.search_companies(
            body=body,
        )

        # Assert response parses correctly
        assert result is not None

        # Assert response type matches expected type
        assert isinstance(result, GetCompanies)

    @settings(
        max_examples=10,
        deadline=None,
        suppress_health_check=[
            HealthCheck.filter_too_much,
            HealthCheck.too_slow,
            HealthCheck.data_too_large,
        ],
    )
    @given(
        response_data=from_schema(
            get_response_schema("/search/companies", "post", "422")
        ),
        body_data=from_schema(get_request_body_schema("/search/companies", "post")),
    )
    def test_search_companies_422_error(
        self,
        backend,
        response_data,
        body_data,
    ):
        """
        Test search_companies with 422 error response.

        HTTP 422 errors raise ClientError.
        """
        # Generate path parameters
        path = "/search/companies"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP error response
        pook.post(url).reply(422).json(response_data).header(
            "Content-Type", "application/json"
        )

        # Parse body_data into Pydantic model
        body = SearchCompanies.model_validate(body_data)

        # HTTP 422 should raise ClientError
        with pytest.raises(ClientError) as exc_info:
            self.sdk.reseller.search_companies(
                body=body,
            )

        # Verify the exception contains the correct status code
        assert exc_info.value.status_code == 422
