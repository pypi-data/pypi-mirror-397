"""
Tests for id service.

Generated from OpenAPI spec version 1.128.5.
Uses property-based testing with hypothesis-jsonschema.
"""

from unittest.mock import Mock
from uuid import uuid4

import pook
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis_jsonschema import from_schema

from satvu import SatVuSDK, create_http_client
from satvu.http.errors import ClientError
from satvu.services.id.models.client_credentials import ClientCredentials
from satvu.services.id.models.client_id import ClientID
from satvu.services.id.models.core_webhook import CoreWebhook
from satvu.services.id.models.create_webhook_response import CreateWebhookResponse
from satvu.services.id.models.edit_webhook_payload import EditWebhookPayload
from satvu.services.id.models.list_webhook_response import ListWebhookResponse
from satvu.services.id.models.post_webhook_response import PostWebhookResponse
from satvu.services.id.models.test_webhook_response import TestWebhookResponse
from satvu.services.id.models.user_info import UserInfo
from satvu.services.id.models.user_settings import UserSettings
from satvu.services.id.models.webhook_response import WebhookResponse

from .test_schemas import (
    get_request_body_schema,
    get_response_schema,
)


@pytest.mark.parametrize("backend", ["stdlib", "httpx", "urllib3", "requests"])
class TestIdService:
    """Property-based tests for IdService."""

    @pytest.fixture(autouse=True)
    def setup(self, backend):
        """Set up test fixtures before each test method."""
        # Mock the auth token
        mock_get_token = Mock(return_value="test_token")

        # Construct base URL for the id service
        # We need to match how SDKClient builds its base_url in __init__
        subdomain = "api"
        env_part = "qa."
        base_path = "/id/v3"
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
        self.sdk.id._get_token = mock_get_token

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
        response_data=from_schema(get_response_schema("/webhooks/", "get", "200")),
    )
    def test_list_webhooks_200(
        self,
        backend,
        response_data,
    ):
        """
        Test list_webhooks with 200 response.
        """
        # Generate path parameters
        path = "/webhooks/"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP response
        pook.get(url).reply(200).json(response_data).header(
            "Content-Type", "application/json"
        )

        # Call the service method

        result = self.sdk.id.list_webhooks()

        # Assert response parses correctly
        assert result is not None

        # Assert response type matches expected type
        assert isinstance(result, ListWebhookResponse)

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
        response_data=from_schema(get_response_schema("/webhooks/", "get", "422")),
    )
    def test_list_webhooks_422_error(
        self,
        backend,
        response_data,
    ):
        """
        Test list_webhooks with 422 error response.

        HTTP 422 errors raise ClientError.
        """
        # Generate path parameters
        path = "/webhooks/"
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
            self.sdk.id.list_webhooks()

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
        response_data=from_schema(get_response_schema("/webhooks/", "post", "200")),
        body_data=from_schema(get_request_body_schema("/webhooks/", "post")),
    )
    def test_create_webhook_200(
        self,
        backend,
        response_data,
        body_data,
    ):
        """
        Test create_webhook with 200 response.
        """
        # Generate path parameters
        path = "/webhooks/"
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
        body = CoreWebhook.model_validate(body_data)

        result = self.sdk.id.create_webhook(
            body=body,
        )

        # Assert response parses correctly
        assert result is not None

        # Assert response type matches expected type
        assert isinstance(result, CreateWebhookResponse)

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
        response_data=from_schema(get_response_schema("/webhooks/", "post", "400")),
        body_data=from_schema(get_request_body_schema("/webhooks/", "post")),
    )
    def test_create_webhook_400_error(
        self,
        backend,
        response_data,
        body_data,
    ):
        """
        Test create_webhook with 400 error response.

        HTTP 400 errors raise ClientError.
        """
        # Generate path parameters
        path = "/webhooks/"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP error response
        pook.post(url).reply(400).json(response_data).header(
            "Content-Type", "application/json"
        )

        # Parse body_data into Pydantic model
        body = CoreWebhook.model_validate(body_data)

        # HTTP 400 should raise ClientError
        with pytest.raises(ClientError) as exc_info:
            self.sdk.id.create_webhook(
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
        response_data=from_schema(get_response_schema("/webhooks/", "post", "403")),
        body_data=from_schema(get_request_body_schema("/webhooks/", "post")),
    )
    def test_create_webhook_403_error(
        self,
        backend,
        response_data,
        body_data,
    ):
        """
        Test create_webhook with 403 error response.

        HTTP 403 errors raise ClientError.
        """
        # Generate path parameters
        path = "/webhooks/"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP error response
        pook.post(url).reply(403).json(response_data).header(
            "Content-Type", "application/json"
        )

        # Parse body_data into Pydantic model
        body = CoreWebhook.model_validate(body_data)

        # HTTP 403 should raise ClientError
        with pytest.raises(ClientError) as exc_info:
            self.sdk.id.create_webhook(
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
        response_data=from_schema(get_response_schema("/webhooks/", "post", "422")),
        body_data=from_schema(get_request_body_schema("/webhooks/", "post")),
    )
    def test_create_webhook_422_error(
        self,
        backend,
        response_data,
        body_data,
    ):
        """
        Test create_webhook with 422 error response.

        HTTP 422 errors raise ClientError.
        """
        # Generate path parameters
        path = "/webhooks/"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP error response
        pook.post(url).reply(422).json(response_data).header(
            "Content-Type", "application/json"
        )

        # Parse body_data into Pydantic model
        body = CoreWebhook.model_validate(body_data)

        # HTTP 422 should raise ClientError
        with pytest.raises(ClientError) as exc_info:
            self.sdk.id.create_webhook(
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
        response_data=from_schema(get_response_schema("/webhooks/{id}", "get", "200")),
    )
    def test_get_webhook_200(
        self,
        backend,
        response_data,
    ):
        """
        Test get_webhook with 200 response.
        """
        # Generate path parameters
        id = uuid4()
        path = f"/webhooks/{id}"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP response
        pook.get(url).reply(200).json(response_data).header(
            "Content-Type", "application/json"
        )

        # Call the service method

        result = self.sdk.id.get_webhook(
            id=id,
        )

        # Assert response parses correctly
        assert result is not None

        # Assert response type matches expected type
        assert isinstance(result, WebhookResponse)

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
        response_data=from_schema(get_response_schema("/webhooks/{id}", "get", "404")),
    )
    def test_get_webhook_404_error(
        self,
        backend,
        response_data,
    ):
        """
        Test get_webhook with 404 error response.

        HTTP 404 errors raise ClientError.
        """
        # Generate path parameters
        id = uuid4()
        path = f"/webhooks/{id}"
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
            self.sdk.id.get_webhook(
                id=id,
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
        response_data=from_schema(get_response_schema("/webhooks/{id}", "get", "422")),
    )
    def test_get_webhook_422_error(
        self,
        backend,
        response_data,
    ):
        """
        Test get_webhook with 422 error response.

        HTTP 422 errors raise ClientError.
        """
        # Generate path parameters
        id = uuid4()
        path = f"/webhooks/{id}"
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
            self.sdk.id.get_webhook(
                id=id,
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
            get_response_schema("/webhooks/{id}", "delete", "404")
        ),
    )
    def test_delete_webhook_404_error(
        self,
        backend,
        response_data,
    ):
        """
        Test delete_webhook with 404 error response.

        HTTP 404 errors raise ClientError.
        """
        # Generate path parameters
        id = uuid4()
        path = f"/webhooks/{id}"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP error response
        pook.delete(url).reply(404).json(response_data).header(
            "Content-Type", "application/json"
        )

        # HTTP 404 should raise ClientError
        with pytest.raises(ClientError) as exc_info:
            self.sdk.id.delete_webhook(
                id=id,
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
            get_response_schema("/webhooks/{id}", "delete", "422")
        ),
    )
    def test_delete_webhook_422_error(
        self,
        backend,
        response_data,
    ):
        """
        Test delete_webhook with 422 error response.

        HTTP 422 errors raise ClientError.
        """
        # Generate path parameters
        id = uuid4()
        path = f"/webhooks/{id}"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP error response
        pook.delete(url).reply(422).json(response_data).header(
            "Content-Type", "application/json"
        )

        # HTTP 422 should raise ClientError
        with pytest.raises(ClientError) as exc_info:
            self.sdk.id.delete_webhook(
                id=id,
            )

        # Verify the exception contains the correct status code
        assert exc_info.value.status_code == 422

    @pook.on
    def test_delete_webhook_204_no_content(
        self,
        backend,
    ):
        """
        Test delete_webhook with 204 No Content response.

        204 responses return None (no body).
        """
        # Generate path parameters
        id = uuid4()
        path = f"/webhooks/{id}"
        url = f"{self.base_url}{path}"

        # Mock the HTTP 204 No Content response
        pook.delete(url).reply(204).header("Content-Type", "application/json")

        # Call the service method
        result = self.sdk.id.delete_webhook(
            id=id,
        )

        # 204 No Content returns None
        assert result is None

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
            get_response_schema("/webhooks/{id}", "patch", "200")
        ),
        body_data=from_schema(get_request_body_schema("/webhooks/{id}", "patch")),
    )
    def test_edit_webhook_200(
        self,
        backend,
        response_data,
        body_data,
    ):
        """
        Test edit_webhook with 200 response.
        """
        # Generate path parameters
        id = uuid4()
        path = f"/webhooks/{id}"
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
        body = EditWebhookPayload.model_validate(body_data)

        result = self.sdk.id.edit_webhook(
            id=id,
            body=body,
        )

        # Assert response parses correctly
        assert result is not None

        # Assert response type matches expected type
        assert isinstance(result, WebhookResponse)

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
            get_response_schema("/webhooks/{id}", "patch", "403")
        ),
        body_data=from_schema(get_request_body_schema("/webhooks/{id}", "patch")),
    )
    def test_edit_webhook_403_error(
        self,
        backend,
        response_data,
        body_data,
    ):
        """
        Test edit_webhook with 403 error response.

        HTTP 403 errors raise ClientError.
        """
        # Generate path parameters
        id = uuid4()
        path = f"/webhooks/{id}"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP error response
        pook.patch(url).reply(403).json(response_data).header(
            "Content-Type", "application/json"
        )

        # Parse body_data into Pydantic model
        body = EditWebhookPayload.model_validate(body_data)

        # HTTP 403 should raise ClientError
        with pytest.raises(ClientError) as exc_info:
            self.sdk.id.edit_webhook(
                id=id,
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
            get_response_schema("/webhooks/{id}", "patch", "404")
        ),
        body_data=from_schema(get_request_body_schema("/webhooks/{id}", "patch")),
    )
    def test_edit_webhook_404_error(
        self,
        backend,
        response_data,
        body_data,
    ):
        """
        Test edit_webhook with 404 error response.

        HTTP 404 errors raise ClientError.
        """
        # Generate path parameters
        id = uuid4()
        path = f"/webhooks/{id}"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP error response
        pook.patch(url).reply(404).json(response_data).header(
            "Content-Type", "application/json"
        )

        # Parse body_data into Pydantic model
        body = EditWebhookPayload.model_validate(body_data)

        # HTTP 404 should raise ClientError
        with pytest.raises(ClientError) as exc_info:
            self.sdk.id.edit_webhook(
                id=id,
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
            get_response_schema("/webhooks/{id}", "patch", "422")
        ),
        body_data=from_schema(get_request_body_schema("/webhooks/{id}", "patch")),
    )
    def test_edit_webhook_422_error(
        self,
        backend,
        response_data,
        body_data,
    ):
        """
        Test edit_webhook with 422 error response.

        HTTP 422 errors raise ClientError.
        """
        # Generate path parameters
        id = uuid4()
        path = f"/webhooks/{id}"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP error response
        pook.patch(url).reply(422).json(response_data).header(
            "Content-Type", "application/json"
        )

        # Parse body_data into Pydantic model
        body = EditWebhookPayload.model_validate(body_data)

        # HTTP 422 should raise ClientError
        with pytest.raises(ClientError) as exc_info:
            self.sdk.id.edit_webhook(
                id=id,
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
            get_response_schema("/webhooks/events", "get", "200")
        ),
    )
    def test_get_webhook_events_200(
        self,
        backend,
        response_data,
    ):
        """
        Test get_webhook_events with 200 response.
        """
        # Generate path parameters
        path = "/webhooks/events"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP response
        pook.get(url).reply(200).json(response_data).header(
            "Content-Type", "application/json"
        )

        # Call the service method

        result = self.sdk.id.get_webhook_events()

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
        response_data=from_schema(
            get_response_schema("/webhooks/{id}/rotate", "post", "200")
        ),
    )
    def test_rotate_webhook_signing_key_200(
        self,
        backend,
        response_data,
    ):
        """
        Test rotate_webhook_signing_key with 200 response.
        """
        # Generate path parameters
        id = uuid4()
        path = f"/webhooks/{id}/rotate"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP response
        pook.post(url).reply(200).json(response_data).header(
            "Content-Type", "application/json"
        )

        # Call the service method

        result = self.sdk.id.rotate_webhook_signing_key(
            id=id,
        )

        # Assert response parses correctly
        assert result is not None

        # Assert response type matches expected type
        assert isinstance(result, PostWebhookResponse)

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
            get_response_schema("/webhooks/{id}/rotate", "post", "404")
        ),
    )
    def test_rotate_webhook_signing_key_404_error(
        self,
        backend,
        response_data,
    ):
        """
        Test rotate_webhook_signing_key with 404 error response.

        HTTP 404 errors raise ClientError.
        """
        # Generate path parameters
        id = uuid4()
        path = f"/webhooks/{id}/rotate"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP error response
        pook.post(url).reply(404).json(response_data).header(
            "Content-Type", "application/json"
        )

        # HTTP 404 should raise ClientError
        with pytest.raises(ClientError) as exc_info:
            self.sdk.id.rotate_webhook_signing_key(
                id=id,
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
            get_response_schema("/webhooks/{id}/rotate", "post", "422")
        ),
    )
    def test_rotate_webhook_signing_key_422_error(
        self,
        backend,
        response_data,
    ):
        """
        Test rotate_webhook_signing_key with 422 error response.

        HTTP 422 errors raise ClientError.
        """
        # Generate path parameters
        id = uuid4()
        path = f"/webhooks/{id}/rotate"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP error response
        pook.post(url).reply(422).json(response_data).header(
            "Content-Type", "application/json"
        )

        # HTTP 422 should raise ClientError
        with pytest.raises(ClientError) as exc_info:
            self.sdk.id.rotate_webhook_signing_key(
                id=id,
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
            get_response_schema("/webhooks/{id}/test", "post", "200")
        ),
    )
    def test_test_webhook_200(
        self,
        backend,
        response_data,
    ):
        """
        Test test_webhook with 200 response.
        """
        # Generate path parameters
        id = uuid4()
        path = f"/webhooks/{id}/test"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP response
        pook.post(url).reply(200).json(response_data).header(
            "Content-Type", "application/json"
        )

        # Call the service method

        result = self.sdk.id.test_webhook(
            id=id,
        )

        # Assert response parses correctly
        assert result is not None

        # Assert response type matches expected type
        assert isinstance(result, TestWebhookResponse)

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
            get_response_schema("/webhooks/{id}/test", "post", "404")
        ),
    )
    def test_test_webhook_404_error(
        self,
        backend,
        response_data,
    ):
        """
        Test test_webhook with 404 error response.

        HTTP 404 errors raise ClientError.
        """
        # Generate path parameters
        id = uuid4()
        path = f"/webhooks/{id}/test"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP error response
        pook.post(url).reply(404).json(response_data).header(
            "Content-Type", "application/json"
        )

        # HTTP 404 should raise ClientError
        with pytest.raises(ClientError) as exc_info:
            self.sdk.id.test_webhook(
                id=id,
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
            get_response_schema("/webhooks/{id}/test", "post", "422")
        ),
    )
    def test_test_webhook_422_error(
        self,
        backend,
        response_data,
    ):
        """
        Test test_webhook with 422 error response.

        HTTP 422 errors raise ClientError.
        """
        # Generate path parameters
        id = uuid4()
        path = f"/webhooks/{id}/test"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP error response
        pook.post(url).reply(422).json(response_data).header(
            "Content-Type", "application/json"
        )

        # HTTP 422 should raise ClientError
        with pytest.raises(ClientError) as exc_info:
            self.sdk.id.test_webhook(
                id=id,
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
        response_data=from_schema(get_response_schema("/client", "get", "200")),
    )
    def test_get_user_client_200(
        self,
        backend,
        response_data,
    ):
        """
        Test get_user_client with 200 response.
        """
        # Generate path parameters
        path = "/client"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP response
        pook.get(url).reply(200).json(response_data).header(
            "Content-Type", "application/json"
        )

        # Call the service method

        result = self.sdk.id.get_user_client()

        # Assert response parses correctly
        assert result is not None

        # Assert response type matches expected type
        assert isinstance(result, ClientID)

    @pook.on
    def test_get_user_client_204_no_content(
        self,
        backend,
    ):
        """
        Test get_user_client with 204 No Content response.

        204 responses return None (no body).
        """
        # Generate path parameters
        path = "/client"
        url = f"{self.base_url}{path}"

        # Mock the HTTP 204 No Content response
        pook.get(url).reply(204).header("Content-Type", "application/json")

        # Call the service method
        result = self.sdk.id.get_user_client()

        # 204 No Content returns None
        assert result is None

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
        response_data=from_schema(get_response_schema("/client", "post", "201")),
    )
    def test_create_user_client_201(
        self,
        backend,
        response_data,
    ):
        """
        Test create_user_client with 201 response.
        """
        # Generate path parameters
        path = "/client"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP response
        pook.post(url).reply(201).json(response_data).header(
            "Content-Type", "application/json"
        )

        # Call the service method

        result = self.sdk.id.create_user_client()

        # Assert response parses correctly
        assert result is not None

        # Assert response type matches expected type
        assert isinstance(result, ClientCredentials)

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
        response_data=from_schema(get_response_schema("/client", "post", "409")),
    )
    def test_create_user_client_409_error(
        self,
        backend,
        response_data,
    ):
        """
        Test create_user_client with 409 error response.

        HTTP 409 errors raise ClientError.
        """
        # Generate path parameters
        path = "/client"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP error response
        pook.post(url).reply(409).json(response_data).header(
            "Content-Type", "application/json"
        )

        # HTTP 409 should raise ClientError
        with pytest.raises(ClientError) as exc_info:
            self.sdk.id.create_user_client()

        # Verify the exception contains the correct status code
        assert exc_info.value.status_code == 409

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
        response_data=from_schema(get_response_schema("/client/reset", "post", "200")),
    )
    def test_rotate_client_secret_200(
        self,
        backend,
        response_data,
    ):
        """
        Test rotate_client_secret with 200 response.
        """
        # Generate path parameters
        path = "/client/reset"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP response
        pook.post(url).reply(200).json(response_data).header(
            "Content-Type", "application/json"
        )

        # Call the service method

        result = self.sdk.id.rotate_client_secret()

        # Assert response parses correctly
        assert result is not None

        # Assert response type matches expected type
        assert isinstance(result, ClientCredentials)

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
        response_data=from_schema(get_response_schema("/client/reset", "post", "404")),
    )
    def test_rotate_client_secret_404_error(
        self,
        backend,
        response_data,
    ):
        """
        Test rotate_client_secret with 404 error response.

        HTTP 404 errors raise ClientError.
        """
        # Generate path parameters
        path = "/client/reset"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP error response
        pook.post(url).reply(404).json(response_data).header(
            "Content-Type", "application/json"
        )

        # HTTP 404 should raise ClientError
        with pytest.raises(ClientError) as exc_info:
            self.sdk.id.rotate_client_secret()

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
        response_data=from_schema(get_response_schema("/user/details", "get", "200")),
    )
    def test_get_user_details_200(
        self,
        backend,
        response_data,
    ):
        """
        Test get_user_details with 200 response.
        """
        # Generate path parameters
        path = "/user/details"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP response
        pook.get(url).reply(200).json(response_data).header(
            "Content-Type", "application/json"
        )

        # Call the service method

        result = self.sdk.id.get_user_details()

        # Assert response parses correctly
        assert result is not None

        # Assert response type matches expected type
        assert isinstance(result, UserInfo)

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
        response_data=from_schema(get_response_schema("/user/settings", "put", "200")),
        body_data=from_schema(get_request_body_schema("/user/settings", "put")),
    )
    def test_edit_user_settings_200(
        self,
        backend,
        response_data,
        body_data,
    ):
        """
        Test edit_user_settings with 200 response.
        """
        # Generate path parameters
        path = "/user/settings"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP response
        pook.put(url).reply(200).json(response_data).header(
            "Content-Type", "application/json"
        )

        # Call the service method
        # Parse body_data into Pydantic model
        body = UserSettings.model_validate(body_data)

        result = self.sdk.id.edit_user_settings(
            body=body,
        )

        # Assert response parses correctly
        assert result is not None

        # Assert response type matches expected type
        assert isinstance(result, UserInfo)

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
        response_data=from_schema(get_response_schema("/user/settings", "put", "422")),
        body_data=from_schema(get_request_body_schema("/user/settings", "put")),
    )
    def test_edit_user_settings_422_error(
        self,
        backend,
        response_data,
        body_data,
    ):
        """
        Test edit_user_settings with 422 error response.

        HTTP 422 errors raise ClientError.
        """
        # Generate path parameters
        path = "/user/settings"
        url = f"{self.base_url}{path}"

        # Reset and activate pook for each hypothesis iteration
        pook.reset()
        pook.on()

        # Mock the HTTP error response
        pook.put(url).reply(422).json(response_data).header(
            "Content-Type", "application/json"
        )

        # Parse body_data into Pydantic model
        body = UserSettings.model_validate(body_data)

        # HTTP 422 should raise ClientError
        with pytest.raises(ClientError) as exc_info:
            self.sdk.id.edit_user_settings(
                body=body,
            )

        # Verify the exception contains the correct status code
        assert exc_info.value.status_code == 422
