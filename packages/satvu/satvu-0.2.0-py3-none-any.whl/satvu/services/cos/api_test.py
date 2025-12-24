"""
Tests for cos service.

Generated from OpenAPI spec version v3.
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
from satvu.services.cos.models.feature_collection_order import FeatureCollectionOrder
from satvu.services.cos.models.order_download_url import OrderDownloadUrl
from satvu.services.cos.models.order_edit_payload import OrderEditPayload
from satvu.services.cos.models.order_item_download_url import OrderItemDownloadUrl
from satvu.services.cos.models.order_page import OrderPage
from satvu.services.cos.models.order_price import OrderPrice
from satvu.services.cos.models.order_submission_payload import OrderSubmissionPayload
from satvu.services.cos.models.price_request import PriceRequest
from satvu.services.cos.models.reseller_feature_collection_order import (
    ResellerFeatureCollectionOrder,
)
from satvu.services.cos.models.reseller_order_price import ResellerOrderPrice
from satvu.services.cos.models.reseller_price_request import ResellerPriceRequest
from satvu.services.cos.models.reseller_submission_order_payload import (
    ResellerSubmissionOrderPayload,
)
from satvu.services.cos.models.search_request import SearchRequest

from .test_schemas import (
    get_request_body_schema,
    get_response_schema,
)


@pytest.mark.parametrize("backend", ["stdlib", "httpx", "urllib3", "requests"])
class TestCosService:
    """Property-based tests for CosService."""

    @pytest.fixture(autouse=True)
    def setup(self, backend):
        """Set up test fixtures before each test method."""
        # Mock the auth token
        mock_get_token = Mock(return_value="test_token")

        # Construct base URL for the cos service
        # We need to match how SDKClient builds its base_url in __init__
        subdomain = "api"
        env_part = "qa."
        base_path = "/orders/v3"
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
        self.sdk.cos._get_token = mock_get_token

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
            get_response_schema("/{contract_id}/{order_id}", "get", "200")
        ),
    )
    def test_get_order_200(
        self,
        backend,
        response_data,
    ):
        """
        Test get_order with 200 response.
        """
        # Generate path parameters
        contract_id = uuid4()
        order_id = uuid4()
        path = f"/{contract_id}/{order_id}"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP response
        pook.get(url).reply(200).json(response_data).header(
            "Content-Type", "application/json"
        )

        # Call the service method

        result = self.sdk.cos.get_order(
            contract_id=contract_id,
            order_id=order_id,
        )

        # Assert response parses correctly
        assert result is not None

        # Assert response type matches expected type
        assert isinstance(
            result, (FeatureCollectionOrder, ResellerFeatureCollectionOrder)
        )

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
            get_response_schema("/{contract_id}/{order_id}", "get", "404")
        ),
    )
    def test_get_order_404_error(
        self,
        backend,
        response_data,
    ):
        """
        Test get_order with 404 error response.

        HTTP 404 errors raise ClientError.
        """
        # Generate path parameters
        contract_id = uuid4()
        order_id = uuid4()
        path = f"/{contract_id}/{order_id}"
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
            self.sdk.cos.get_order(
                contract_id=contract_id,
                order_id=order_id,
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
            get_response_schema("/{contract_id}/{order_id}", "get", "422")
        ),
    )
    def test_get_order_422_error(
        self,
        backend,
        response_data,
    ):
        """
        Test get_order with 422 error response.

        HTTP 422 errors raise ClientError.
        """
        # Generate path parameters
        contract_id = uuid4()
        order_id = uuid4()
        path = f"/{contract_id}/{order_id}"
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
            self.sdk.cos.get_order(
                contract_id=contract_id,
                order_id=order_id,
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
            get_response_schema("/{contract_id}/{order_id}", "patch", "200")
        ),
        body_data=from_schema(
            get_request_body_schema("/{contract_id}/{order_id}", "patch")
        ),
    )
    def test_edit_order_200(
        self,
        backend,
        response_data,
        body_data,
    ):
        """
        Test edit_order with 200 response.
        """
        # Generate path parameters
        contract_id = uuid4()
        order_id = uuid4()
        path = f"/{contract_id}/{order_id}"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP response
        pook.patch(url).reply(200).json(response_data).header(
            "Content-Type", "application/json"
        )

        # Call the service method
        # Parse body_data into Pydantic model
        body = OrderEditPayload.model_validate(body_data)

        result = self.sdk.cos.edit_order(
            contract_id=contract_id,
            order_id=order_id,
            body=body,
        )

        # Assert response parses correctly
        assert result is not None

        # Assert response type matches expected type
        assert isinstance(
            result, (FeatureCollectionOrder, ResellerFeatureCollectionOrder)
        )

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
            get_response_schema("/{contract_id}/{order_id}", "patch", "404")
        ),
        body_data=from_schema(
            get_request_body_schema("/{contract_id}/{order_id}", "patch")
        ),
    )
    def test_edit_order_404_error(
        self,
        backend,
        response_data,
        body_data,
    ):
        """
        Test edit_order with 404 error response.

        HTTP 404 errors raise ClientError.
        """
        # Generate path parameters
        contract_id = uuid4()
        order_id = uuid4()
        path = f"/{contract_id}/{order_id}"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP error response
        pook.patch(url).reply(404).json(response_data).header(
            "Content-Type", "application/json"
        )

        # Parse body_data into Pydantic model
        body = OrderEditPayload.model_validate(body_data)

        # HTTP 404 should raise ClientError
        with pytest.raises(ClientError) as exc_info:
            self.sdk.cos.edit_order(
                contract_id=contract_id,
                order_id=order_id,
                body=body,
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
            get_response_schema("/{contract_id}/{order_id}", "patch", "422")
        ),
        body_data=from_schema(
            get_request_body_schema("/{contract_id}/{order_id}", "patch")
        ),
    )
    def test_edit_order_422_error(
        self,
        backend,
        response_data,
        body_data,
    ):
        """
        Test edit_order with 422 error response.

        HTTP 422 errors raise ClientError.
        """
        # Generate path parameters
        contract_id = uuid4()
        order_id = uuid4()
        path = f"/{contract_id}/{order_id}"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP error response
        pook.patch(url).reply(422).json(response_data).header(
            "Content-Type", "application/json"
        )

        # Parse body_data into Pydantic model
        body = OrderEditPayload.model_validate(body_data)

        # HTTP 422 should raise ClientError
        with pytest.raises(ClientError) as exc_info:
            self.sdk.cos.edit_order(
                contract_id=contract_id,
                order_id=order_id,
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
        response_data=from_schema(get_response_schema("/{contract_id}/", "get", "200")),
    )
    def test_query_orders_200(
        self,
        backend,
        response_data,
    ):
        """
        Test query_orders with 200 response.
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

        result = self.sdk.cos.query_orders(
            contract_id=contract_id,
        )

        # Assert response parses correctly
        assert result is not None

        # Assert response type matches expected type
        assert isinstance(result, OrderPage)

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
        response_data=from_schema(get_response_schema("/{contract_id}/", "get", "422")),
    )
    def test_query_orders_422_error(
        self,
        backend,
        response_data,
    ):
        """
        Test query_orders with 422 error response.

        HTTP 422 errors raise ClientError.
        """
        # Generate path parameters
        contract_id = uuid4()
        path = f"/{contract_id}/"
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
            self.sdk.cos.query_orders(
                contract_id=contract_id,
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
            get_response_schema("/{contract_id}/", "post", "201")
        ),
        body_data=from_schema(get_request_body_schema("/{contract_id}/", "post")),
    )
    def test_submit_order_201(
        self,
        backend,
        response_data,
        body_data,
    ):
        """
        Test submit_order with 201 response.
        """
        # Generate path parameters
        contract_id = uuid4()
        path = f"/{contract_id}/"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP response
        pook.post(url).reply(201).json(response_data).header(
            "Content-Type", "application/json"
        )

        # Call the service method
        # For Union types, use TypeAdapter to validate
        body_adapter = TypeAdapter(
            Union[OrderSubmissionPayload, ResellerSubmissionOrderPayload]
        )
        body = body_adapter.validate_python(body_data)

        result = self.sdk.cos.submit_order(
            contract_id=contract_id,
            body=body,
        )

        # Assert response parses correctly
        assert result is not None

        # Assert response type matches expected type
        assert isinstance(
            result, (FeatureCollectionOrder, ResellerFeatureCollectionOrder)
        )

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
            get_response_schema("/{contract_id}/", "post", "400")
        ),
        body_data=from_schema(get_request_body_schema("/{contract_id}/", "post")),
    )
    def test_submit_order_400_error(
        self,
        backend,
        response_data,
        body_data,
    ):
        """
        Test submit_order with 400 error response.

        HTTP 400 errors raise ClientError.
        """
        # Generate path parameters
        contract_id = uuid4()
        path = f"/{contract_id}/"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP error response
        pook.post(url).reply(400).json(response_data).header(
            "Content-Type", "application/json"
        )

        # For Union types, use TypeAdapter to validate
        body_adapter = TypeAdapter(
            Union[OrderSubmissionPayload, ResellerSubmissionOrderPayload]
        )
        body = body_adapter.validate_python(body_data)

        # HTTP 400 should raise ClientError
        with pytest.raises(ClientError) as exc_info:
            self.sdk.cos.submit_order(
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
            get_response_schema("/{contract_id}/", "post", "402")
        ),
        body_data=from_schema(get_request_body_schema("/{contract_id}/", "post")),
    )
    def test_submit_order_402_error(
        self,
        backend,
        response_data,
        body_data,
    ):
        """
        Test submit_order with 402 error response.

        HTTP 402 errors raise ClientError.
        """
        # Generate path parameters
        contract_id = uuid4()
        path = f"/{contract_id}/"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP error response
        pook.post(url).reply(402).json(response_data).header(
            "Content-Type", "application/json"
        )

        # For Union types, use TypeAdapter to validate
        body_adapter = TypeAdapter(
            Union[OrderSubmissionPayload, ResellerSubmissionOrderPayload]
        )
        body = body_adapter.validate_python(body_data)

        # HTTP 402 should raise ClientError
        with pytest.raises(ClientError) as exc_info:
            self.sdk.cos.submit_order(
                contract_id=contract_id,
                body=body,
            )

        # Verify the exception contains the correct status code
        assert exc_info.value.status_code == 402

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
            get_response_schema("/{contract_id}/", "post", "403")
        ),
        body_data=from_schema(get_request_body_schema("/{contract_id}/", "post")),
    )
    def test_submit_order_403_error(
        self,
        backend,
        response_data,
        body_data,
    ):
        """
        Test submit_order with 403 error response.

        HTTP 403 errors raise ClientError.
        """
        # Generate path parameters
        contract_id = uuid4()
        path = f"/{contract_id}/"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP error response
        pook.post(url).reply(403).json(response_data).header(
            "Content-Type", "application/json"
        )

        # For Union types, use TypeAdapter to validate
        body_adapter = TypeAdapter(
            Union[OrderSubmissionPayload, ResellerSubmissionOrderPayload]
        )
        body = body_adapter.validate_python(body_data)

        # HTTP 403 should raise ClientError
        with pytest.raises(ClientError) as exc_info:
            self.sdk.cos.submit_order(
                contract_id=contract_id,
                body=body,
            )

        # Verify the exception contains the correct status code
        assert exc_info.value.status_code == 403

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
            get_response_schema("/{contract_id}/", "post", "422")
        ),
        body_data=from_schema(get_request_body_schema("/{contract_id}/", "post")),
    )
    def test_submit_order_422_error(
        self,
        backend,
        response_data,
        body_data,
    ):
        """
        Test submit_order with 422 error response.

        HTTP 422 errors raise ClientError.
        """
        # Generate path parameters
        contract_id = uuid4()
        path = f"/{contract_id}/"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP error response
        pook.post(url).reply(422).json(response_data).header(
            "Content-Type", "application/json"
        )

        # For Union types, use TypeAdapter to validate
        body_adapter = TypeAdapter(
            Union[OrderSubmissionPayload, ResellerSubmissionOrderPayload]
        )
        body = body_adapter.validate_python(body_data)

        # HTTP 422 should raise ClientError
        with pytest.raises(ClientError) as exc_info:
            self.sdk.cos.submit_order(
                contract_id=contract_id,
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
            get_response_schema("/{contract_id}/search/", "post", "200")
        ),
        body_data=from_schema(
            get_request_body_schema("/{contract_id}/search/", "post")
        ),
    )
    def test_search_orders_200(
        self,
        backend,
        response_data,
        body_data,
    ):
        """
        Test search_orders with 200 response.
        """
        # Generate path parameters
        contract_id = uuid4()
        path = f"/{contract_id}/search/"
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
        body = SearchRequest.model_validate(body_data)

        result = self.sdk.cos.search_orders(
            contract_id=contract_id,
            body=body,
        )

        # Assert response parses correctly
        assert result is not None

        # Assert response type matches expected type
        assert isinstance(result, OrderPage)

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
            get_response_schema("/{contract_id}/search/", "post", "422")
        ),
        body_data=from_schema(
            get_request_body_schema("/{contract_id}/search/", "post")
        ),
    )
    def test_search_orders_422_error(
        self,
        backend,
        response_data,
        body_data,
    ):
        """
        Test search_orders with 422 error response.

        HTTP 422 errors raise ClientError.
        """
        # Generate path parameters
        contract_id = uuid4()
        path = f"/{contract_id}/search/"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP error response
        pook.post(url).reply(422).json(response_data).header(
            "Content-Type", "application/json"
        )

        # Parse body_data into Pydantic model
        body = SearchRequest.model_validate(body_data)

        # HTTP 422 should raise ClientError
        with pytest.raises(ClientError) as exc_info:
            self.sdk.cos.search_orders(
                contract_id=contract_id,
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
            get_response_schema(
                "/{contract_id}/{order_id}/{item_id}/download", "get", "200"
            )
        ),
    )
    def test_download_order_item_200(
        self,
        backend,
        response_data,
    ):
        """
        Test download_order_item with 200 response.
        """
        # Generate path parameters
        contract_id = uuid4()
        order_id = uuid4()
        item_id = uuid4()
        path = f"/{contract_id}/{order_id}/{item_id}/download"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP response
        pook.get(url).reply(200).json(response_data).header(
            "Content-Type", "application/json"
        )

        # Call the service method

        result = self.sdk.cos.download_order_item(
            contract_id=contract_id,
            order_id=order_id,
            item_id=item_id,
        )

        # Assert response parses correctly
        assert result is not None

        # Assert response type matches expected type
        assert isinstance(result, OrderItemDownloadUrl)

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
                "/{contract_id}/{order_id}/{item_id}/download", "get", "404"
            )
        ),
    )
    def test_download_order_item_404_error(
        self,
        backend,
        response_data,
    ):
        """
        Test download_order_item with 404 error response.

        HTTP 404 errors raise ClientError.
        """
        # Generate path parameters
        contract_id = uuid4()
        order_id = uuid4()
        item_id = uuid4()
        path = f"/{contract_id}/{order_id}/{item_id}/download"
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
            self.sdk.cos.download_order_item(
                contract_id=contract_id,
                order_id=order_id,
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
                "/{contract_id}/{order_id}/{item_id}/download", "get", "422"
            )
        ),
    )
    def test_download_order_item_422_error(
        self,
        backend,
        response_data,
    ):
        """
        Test download_order_item with 422 error response.

        HTTP 422 errors raise ClientError.
        """
        # Generate path parameters
        contract_id = uuid4()
        order_id = uuid4()
        item_id = uuid4()
        path = f"/{contract_id}/{order_id}/{item_id}/download"
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
            self.sdk.cos.download_order_item(
                contract_id=contract_id,
                order_id=order_id,
                item_id=item_id,
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
            get_response_schema("/{contract_id}/{order_id}/download", "get", "200")
        ),
    )
    def test_download_order_200(
        self,
        backend,
        response_data,
    ):
        """
        Test download_order with 200 response.
        """
        # Generate path parameters
        contract_id = uuid4()
        order_id = uuid4()
        path = f"/{contract_id}/{order_id}/download"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP response
        pook.get(url).reply(200).json(response_data).header(
            "Content-Type", "application/json"
        )

        # Call the service method

        result = self.sdk.cos.download_order(
            contract_id=contract_id,
            order_id=order_id,
        )

        # Assert response parses correctly
        assert result is not None

        # Assert response type matches expected type
        assert isinstance(result, OrderDownloadUrl)

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
            get_response_schema("/{contract_id}/{order_id}/download", "get", "404")
        ),
    )
    def test_download_order_404_error(
        self,
        backend,
        response_data,
    ):
        """
        Test download_order with 404 error response.

        HTTP 404 errors raise ClientError.
        """
        # Generate path parameters
        contract_id = uuid4()
        order_id = uuid4()
        path = f"/{contract_id}/{order_id}/download"
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
            self.sdk.cos.download_order(
                contract_id=contract_id,
                order_id=order_id,
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
            get_response_schema("/{contract_id}/{order_id}/download", "get", "422")
        ),
    )
    def test_download_order_422_error(
        self,
        backend,
        response_data,
    ):
        """
        Test download_order with 422 error response.

        HTTP 422 errors raise ClientError.
        """
        # Generate path parameters
        contract_id = uuid4()
        order_id = uuid4()
        path = f"/{contract_id}/{order_id}/download"
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
            self.sdk.cos.download_order(
                contract_id=contract_id,
                order_id=order_id,
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
            get_response_schema("/{contract_id}/price", "post", "200")
        ),
        body_data=from_schema(get_request_body_schema("/{contract_id}/price", "post")),
    )
    def test_calculate_price_200(
        self,
        backend,
        response_data,
        body_data,
    ):
        """
        Test calculate_price with 200 response.
        """
        # Generate path parameters
        contract_id = uuid4()
        path = f"/{contract_id}/price"
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
        body_adapter = TypeAdapter(Union[PriceRequest, ResellerPriceRequest])
        body = body_adapter.validate_python(body_data)

        result = self.sdk.cos.calculate_price(
            contract_id=contract_id,
            body=body,
        )

        # Assert response parses correctly
        assert result is not None

        # Assert response type matches expected type
        assert isinstance(result, (OrderPrice, ResellerOrderPrice))

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
            get_response_schema("/{contract_id}/price", "post", "422")
        ),
        body_data=from_schema(get_request_body_schema("/{contract_id}/price", "post")),
    )
    def test_calculate_price_422_error(
        self,
        backend,
        response_data,
        body_data,
    ):
        """
        Test calculate_price with 422 error response.

        HTTP 422 errors raise ClientError.
        """
        # Generate path parameters
        contract_id = uuid4()
        path = f"/{contract_id}/price"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP error response
        pook.post(url).reply(422).json(response_data).header(
            "Content-Type", "application/json"
        )

        # For Union types, use TypeAdapter to validate
        body_adapter = TypeAdapter(Union[PriceRequest, ResellerPriceRequest])
        body = body_adapter.validate_python(body_data)

        # HTTP 422 should raise ClientError
        with pytest.raises(ClientError) as exc_info:
            self.sdk.cos.calculate_price(
                contract_id=contract_id,
                body=body,
            )

        # Verify the exception contains the correct status code
        assert exc_info.value.status_code == 422
