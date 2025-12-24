"""
Tests for catalog service.

Generated from OpenAPI spec version v0.120.0.
Uses property-based testing with hypothesis-jsonschema.
"""

from typing import Union
from unittest.mock import Mock
from uuid import uuid4

import pook
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis_jsonschema import from_schema
from pydantic import TypeAdapter

from satvu import SatVuSDK, create_http_client
from satvu.http.errors import ClientError
from satvu.services.catalog.models.catalog import Catalog
from satvu.services.catalog.models.collection import Collection
from satvu.services.catalog.models.collections import Collections
from satvu.services.catalog.models.conformance import Conformance
from satvu.services.catalog.models.cql_2_queryables_schema import Cql2QueryablesSchema
from satvu.services.catalog.models.feature import Feature
from satvu.services.catalog.models.feature_collection import FeatureCollection
from satvu.services.catalog.models.post_search_input import PostSearchInput
from satvu.services.catalog.models.search_response import SearchResponse

from .test_schemas import (
    get_request_body_schema,
    get_response_schema,
)


@pytest.mark.parametrize("backend", ["stdlib", "httpx", "urllib3", "requests"])
class TestCatalogService:
    """Property-based tests for CatalogService."""

    @pytest.fixture(autouse=True)
    def setup(self, backend):
        """Set up test fixtures before each test method."""
        # Mock the auth token
        mock_get_token = Mock(return_value="test_token")

        # Construct base URL for the catalog service
        # We need to match how SDKClient builds its base_url in __init__
        subdomain = "api"
        env_part = "qa."
        base_path = "/catalog/v1"
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
        self.sdk.catalog._get_token = mock_get_token

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
        response_data=from_schema(get_response_schema("/{contract_id}/", "get", "200")),
    )
    def test_landing_page_200(
        self,
        backend,
        response_data,
    ):
        """
        Test landing_page with 200 response.
        """
        # Generate path parameters
        contract_id = uuid4()
        path = f"/{contract_id}/"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP response
        pook.get(url).reply(200).json(response_data).header(
            "Content-Type", "application/json"
        )

        # Call the service method

        result = self.sdk.catalog.landing_page(
            contract_id=contract_id,
        )

        # Assert response parses correctly
        assert result is not None

        # Assert response type matches expected type
        assert isinstance(result, Catalog)

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
        response_data=from_schema(get_response_schema("/{contract_id}/", "get", "429")),
    )
    def test_landing_page_429_error(
        self,
        backend,
        response_data,
    ):
        """
        Test landing_page with 429 error response.

        HTTP 429 errors raise ClientError.
        """
        # Generate path parameters
        contract_id = uuid4()
        path = f"/{contract_id}/"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP error response
        pook.get(url).reply(429).json(response_data).header(
            "Content-Type", "application/json"
        )

        # HTTP 429 should raise ClientError
        with pytest.raises(ClientError) as exc_info:
            self.sdk.catalog.landing_page(
                contract_id=contract_id,
            )

        # Verify the exception contains the correct status code
        assert exc_info.value.status_code == 429

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
            get_response_schema("/{contract_id}/conformance", "get", "200")
        ),
    )
    def test_conformance_200(
        self,
        backend,
        response_data,
    ):
        """
        Test conformance with 200 response.
        """
        # Generate path parameters
        contract_id = uuid4()
        path = f"/{contract_id}/conformance"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP response
        pook.get(url).reply(200).json(response_data).header(
            "Content-Type", "application/json"
        )

        # Call the service method

        result = self.sdk.catalog.conformance(
            contract_id=contract_id,
        )

        # Assert response parses correctly
        assert result is not None

        # Assert response type matches expected type
        assert isinstance(result, Conformance)

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
            get_response_schema("/{contract_id}/conformance", "get", "429")
        ),
    )
    def test_conformance_429_error(
        self,
        backend,
        response_data,
    ):
        """
        Test conformance with 429 error response.

        HTTP 429 errors raise ClientError.
        """
        # Generate path parameters
        contract_id = uuid4()
        path = f"/{contract_id}/conformance"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP error response
        pook.get(url).reply(429).json(response_data).header(
            "Content-Type", "application/json"
        )

        # HTTP 429 should raise ClientError
        with pytest.raises(ClientError) as exc_info:
            self.sdk.catalog.conformance(
                contract_id=contract_id,
            )

        # Verify the exception contains the correct status code
        assert exc_info.value.status_code == 429

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
            get_response_schema("/{contract_id}/queryables", "get", "200")
        ),
    )
    def test_queryables_200(
        self,
        backend,
        response_data,
    ):
        """
        Test queryables with 200 response.
        """
        # Generate path parameters
        contract_id = uuid4()
        path = f"/{contract_id}/queryables"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP response
        pook.get(url).reply(200).json(response_data).header(
            "Content-Type", "application/json"
        )

        # Call the service method

        result = self.sdk.catalog.queryables(
            contract_id=contract_id,
        )

        # Assert response parses correctly
        assert result is not None

        # Assert response type matches expected type
        assert isinstance(result, Cql2QueryablesSchema)

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
            get_response_schema("/{contract_id}/queryables", "get", "429")
        ),
    )
    def test_queryables_429_error(
        self,
        backend,
        response_data,
    ):
        """
        Test queryables with 429 error response.

        HTTP 429 errors raise ClientError.
        """
        # Generate path parameters
        contract_id = uuid4()
        path = f"/{contract_id}/queryables"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP error response
        pook.get(url).reply(429).json(response_data).header(
            "Content-Type", "application/json"
        )

        # HTTP 429 should raise ClientError
        with pytest.raises(ClientError) as exc_info:
            self.sdk.catalog.queryables(
                contract_id=contract_id,
            )

        # Verify the exception contains the correct status code
        assert exc_info.value.status_code == 429

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
            get_response_schema("/{contract_id}/search", "get", "200")
        ),
    )
    def test_get_search_200(
        self,
        backend,
        response_data,
    ):
        """
        Test get_search with 200 response.
        """
        # Generate path parameters
        contract_id = uuid4()
        path = f"/{contract_id}/search"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP response
        pook.get(url).reply(200).json(response_data).header(
            "Content-Type", "application/json"
        )

        # Call the service method

        result = self.sdk.catalog.get_search(
            contract_id=contract_id,
        )

        # Assert response parses correctly
        assert result is not None

        # Assert response type matches expected type
        assert isinstance(result, FeatureCollection)

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
            get_response_schema("/{contract_id}/search", "get", "400")
        ),
    )
    def test_get_search_400_error(
        self,
        backend,
        response_data,
    ):
        """
        Test get_search with 400 error response.

        HTTP 400 errors raise ClientError.
        """
        # Generate path parameters
        contract_id = uuid4()
        path = f"/{contract_id}/search"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP error response
        pook.get(url).reply(400).json(response_data).header(
            "Content-Type", "application/json"
        )

        # HTTP 400 should raise ClientError
        with pytest.raises(ClientError) as exc_info:
            self.sdk.catalog.get_search(
                contract_id=contract_id,
            )

        # Verify the exception contains the correct status code
        assert exc_info.value.status_code == 400

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
            get_response_schema("/{contract_id}/search", "get", "429")
        ),
    )
    def test_get_search_429_error(
        self,
        backend,
        response_data,
    ):
        """
        Test get_search with 429 error response.

        HTTP 429 errors raise ClientError.
        """
        # Generate path parameters
        contract_id = uuid4()
        path = f"/{contract_id}/search"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP error response
        pook.get(url).reply(429).json(response_data).header(
            "Content-Type", "application/json"
        )

        # HTTP 429 should raise ClientError
        with pytest.raises(ClientError) as exc_info:
            self.sdk.catalog.get_search(
                contract_id=contract_id,
            )

        # Verify the exception contains the correct status code
        assert exc_info.value.status_code == 429

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
            get_response_schema("/{contract_id}/search", "post", "200")
        ),
        body_data=from_schema(get_request_body_schema("/{contract_id}/search", "post")),
    )
    def test_post_search_200(
        self,
        backend,
        response_data,
        body_data,
    ):
        """
        Test post_search with 200 response.
        """
        # Generate path parameters
        contract_id = uuid4()
        path = f"/{contract_id}/search"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP response
        pook.post(url).reply(200).json(response_data).header(
            "Content-Type", "application/json"
        )

        # Call the service method
        # For Union types, use TypeAdapter to validate
        body_adapter = TypeAdapter(Union[None, PostSearchInput])
        body = body_adapter.validate_python(body_data)

        result = self.sdk.catalog.post_search(
            contract_id=contract_id,
            body=body,
        )

        # Assert response parses correctly
        assert result is not None

        # Assert response type matches expected type
        assert isinstance(result, FeatureCollection)

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
            get_response_schema("/{contract_id}/search", "post", "400")
        ),
        body_data=from_schema(get_request_body_schema("/{contract_id}/search", "post")),
    )
    def test_post_search_400_error(
        self,
        backend,
        response_data,
        body_data,
    ):
        """
        Test post_search with 400 error response.

        HTTP 400 errors raise ClientError.
        """
        # Generate path parameters
        contract_id = uuid4()
        path = f"/{contract_id}/search"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP error response
        pook.post(url).reply(400).json(response_data).header(
            "Content-Type", "application/json"
        )

        # For Union types, use TypeAdapter to validate
        body_adapter = TypeAdapter(Union[None, PostSearchInput])
        body = body_adapter.validate_python(body_data)

        # HTTP 400 should raise ClientError
        with pytest.raises(ClientError) as exc_info:
            self.sdk.catalog.post_search(
                contract_id=contract_id,
                body=body,
            )

        # Verify the exception contains the correct status code
        assert exc_info.value.status_code == 400

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
            get_response_schema("/{contract_id}/search", "post", "429")
        ),
        body_data=from_schema(get_request_body_schema("/{contract_id}/search", "post")),
    )
    def test_post_search_429_error(
        self,
        backend,
        response_data,
        body_data,
    ):
        """
        Test post_search with 429 error response.

        HTTP 429 errors raise ClientError.
        """
        # Generate path parameters
        contract_id = uuid4()
        path = f"/{contract_id}/search"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP error response
        pook.post(url).reply(429).json(response_data).header(
            "Content-Type", "application/json"
        )

        # For Union types, use TypeAdapter to validate
        body_adapter = TypeAdapter(Union[None, PostSearchInput])
        body = body_adapter.validate_python(body_data)

        # HTTP 429 should raise ClientError
        with pytest.raises(ClientError) as exc_info:
            self.sdk.catalog.post_search(
                contract_id=contract_id,
                body=body,
            )

        # Verify the exception contains the correct status code
        assert exc_info.value.status_code == 429

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
            get_response_schema("/{contract_id}/collections", "get", "200")
        ),
    )
    def test_get_collections_200(
        self,
        backend,
        response_data,
    ):
        """
        Test get_collections with 200 response.
        """
        # Generate path parameters
        contract_id = uuid4()
        path = f"/{contract_id}/collections"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP response
        pook.get(url).reply(200).json(response_data).header(
            "Content-Type", "application/json"
        )

        # Call the service method

        result = self.sdk.catalog.get_collections(
            contract_id=contract_id,
        )

        # Assert response parses correctly
        assert result is not None

        # Assert response type matches expected type
        assert isinstance(result, Collections)

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
            get_response_schema("/{contract_id}/collections", "get", "429")
        ),
    )
    def test_get_collections_429_error(
        self,
        backend,
        response_data,
    ):
        """
        Test get_collections with 429 error response.

        HTTP 429 errors raise ClientError.
        """
        # Generate path parameters
        contract_id = uuid4()
        path = f"/{contract_id}/collections"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP error response
        pook.get(url).reply(429).json(response_data).header(
            "Content-Type", "application/json"
        )

        # HTTP 429 should raise ClientError
        with pytest.raises(ClientError) as exc_info:
            self.sdk.catalog.get_collections(
                contract_id=contract_id,
            )

        # Verify the exception contains the correct status code
        assert exc_info.value.status_code == 429

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
            get_response_schema(
                "/{contract_id}/collections/{collection_id}", "get", "200"
            )
        ),
    )
    def test_get_collection_200(
        self,
        backend,
        response_data,
    ):
        """
        Test get_collection with 200 response.
        """
        # Generate path parameters
        contract_id = uuid4()
        collection_id = uuid4()
        path = f"/{contract_id}/collections/{collection_id}"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP response
        pook.get(url).reply(200).json(response_data).header(
            "Content-Type", "application/json"
        )

        # Call the service method

        result = self.sdk.catalog.get_collection(
            contract_id=contract_id,
            collection_id=collection_id,
        )

        # Assert response parses correctly
        assert result is not None

        # Assert response type matches expected type
        assert isinstance(result, Collection)

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
            get_response_schema(
                "/{contract_id}/collections/{collection_id}", "get", "404"
            )
        ),
    )
    def test_get_collection_404_error(
        self,
        backend,
        response_data,
    ):
        """
        Test get_collection with 404 error response.

        HTTP 404 errors raise ClientError.
        """
        # Generate path parameters
        contract_id = uuid4()
        collection_id = uuid4()
        path = f"/{contract_id}/collections/{collection_id}"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP error response
        pook.get(url).reply(404).json(response_data).header(
            "Content-Type", "application/json"
        )

        # HTTP 404 should raise ClientError
        with pytest.raises(ClientError) as exc_info:
            self.sdk.catalog.get_collection(
                contract_id=contract_id,
                collection_id=collection_id,
            )

        # Verify the exception contains the correct status code
        assert exc_info.value.status_code == 404

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
            get_response_schema(
                "/{contract_id}/collections/{collection_id}", "get", "429"
            )
        ),
    )
    def test_get_collection_429_error(
        self,
        backend,
        response_data,
    ):
        """
        Test get_collection with 429 error response.

        HTTP 429 errors raise ClientError.
        """
        # Generate path parameters
        contract_id = uuid4()
        collection_id = uuid4()
        path = f"/{contract_id}/collections/{collection_id}"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP error response
        pook.get(url).reply(429).json(response_data).header(
            "Content-Type", "application/json"
        )

        # HTTP 429 should raise ClientError
        with pytest.raises(ClientError) as exc_info:
            self.sdk.catalog.get_collection(
                contract_id=contract_id,
                collection_id=collection_id,
            )

        # Verify the exception contains the correct status code
        assert exc_info.value.status_code == 429

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
            get_response_schema(
                "/{contract_id}/collections/{collection_id}/items", "get", "200"
            )
        ),
    )
    def test_get_item_collection_200(
        self,
        backend,
        response_data,
    ):
        """
        Test get_item_collection with 200 response.
        """
        # Generate path parameters
        contract_id = uuid4()
        collection_id = uuid4()
        path = f"/{contract_id}/collections/{collection_id}/items"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP response
        pook.get(url).reply(200).json(response_data).header(
            "Content-Type", "application/json"
        )

        # Call the service method

        result = self.sdk.catalog.get_item_collection(
            contract_id=contract_id,
            collection_id=collection_id,
        )

        # Assert response parses correctly
        assert result is not None

        # Assert response type matches expected type
        assert isinstance(result, SearchResponse)

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
            get_response_schema(
                "/{contract_id}/collections/{collection_id}/items", "get", "429"
            )
        ),
    )
    def test_get_item_collection_429_error(
        self,
        backend,
        response_data,
    ):
        """
        Test get_item_collection with 429 error response.

        HTTP 429 errors raise ClientError.
        """
        # Generate path parameters
        contract_id = uuid4()
        collection_id = uuid4()
        path = f"/{contract_id}/collections/{collection_id}/items"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP error response
        pook.get(url).reply(429).json(response_data).header(
            "Content-Type", "application/json"
        )

        # HTTP 429 should raise ClientError
        with pytest.raises(ClientError) as exc_info:
            self.sdk.catalog.get_item_collection(
                contract_id=contract_id,
                collection_id=collection_id,
            )

        # Verify the exception contains the correct status code
        assert exc_info.value.status_code == 429

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
            get_response_schema(
                "/{contract_id}/collections/{collection_id}/{item_id}", "get", "200"
            )
        ),
    )
    def test_get_item_200(
        self,
        backend,
        response_data,
    ):
        """
        Test get_item with 200 response.
        """
        # Generate path parameters
        contract_id = uuid4()
        collection_id = uuid4()
        item_id = uuid4()
        path = f"/{contract_id}/collections/{collection_id}/{item_id}"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP response
        pook.get(url).reply(200).json(response_data).header(
            "Content-Type", "application/json"
        )

        # Call the service method

        result = self.sdk.catalog.get_item(
            contract_id=contract_id,
            collection_id=collection_id,
            item_id=item_id,
        )

        # Assert response parses correctly
        assert result is not None

        # Assert response type matches expected type
        assert isinstance(result, Feature)

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
            get_response_schema(
                "/{contract_id}/collections/{collection_id}/{item_id}", "get", "404"
            )
        ),
    )
    def test_get_item_404_error(
        self,
        backend,
        response_data,
    ):
        """
        Test get_item with 404 error response.

        HTTP 404 errors raise ClientError.
        """
        # Generate path parameters
        contract_id = uuid4()
        collection_id = uuid4()
        item_id = uuid4()
        path = f"/{contract_id}/collections/{collection_id}/{item_id}"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP error response
        pook.get(url).reply(404).json(response_data).header(
            "Content-Type", "application/json"
        )

        # HTTP 404 should raise ClientError
        with pytest.raises(ClientError) as exc_info:
            self.sdk.catalog.get_item(
                contract_id=contract_id,
                collection_id=collection_id,
                item_id=item_id,
            )

        # Verify the exception contains the correct status code
        assert exc_info.value.status_code == 404

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
            get_response_schema(
                "/{contract_id}/collections/{collection_id}/{item_id}", "get", "429"
            )
        ),
    )
    def test_get_item_429_error(
        self,
        backend,
        response_data,
    ):
        """
        Test get_item with 429 error response.

        HTTP 429 errors raise ClientError.
        """
        # Generate path parameters
        contract_id = uuid4()
        collection_id = uuid4()
        item_id = uuid4()
        path = f"/{contract_id}/collections/{collection_id}/{item_id}"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP error response
        pook.get(url).reply(429).json(response_data).header(
            "Content-Type", "application/json"
        )

        # HTTP 429 should raise ClientError
        with pytest.raises(ClientError) as exc_info:
            self.sdk.catalog.get_item(
                contract_id=contract_id,
                collection_id=collection_id,
                item_id=item_id,
            )

        # Verify the exception contains the correct status code
        assert exc_info.value.status_code == 429
