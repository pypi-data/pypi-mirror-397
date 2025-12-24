"""
Schemas for wallet service tests.

Generated from OpenAPI spec version 0.0.1.
These schemas are used with hypothesis-jsonschema to generate test data.

Stores entire OpenAPI spec as operations with helper functions for access.
"""

# Component schemas for $ref resolution (cleaned for JSON Schema draft-07)
_COMPONENTS = {
    "BatchBalanceResponse": {
        "properties": {
            "balances": {
                "additionalProperties": {"$ref": "#/definitions/CreditBalanceResponse"},
                "description": "Mapping "
                "of "
                "contract "
                "IDs to "
                "their "
                "credit "
                "balance "
                "responses",
                "propertyNames": {"format": "uuid"},
                "title": "Balances",
                "type": "object",
            }
        },
        "required": ["balances"],
        "title": "BatchBalanceResponse",
        "type": "object",
    },
    "CreditBalanceResponse": {
        "properties": {
            "balance": {
                "description": "The "
                "credit "
                "balance "
                "of the "
                "user, in "
                "minor "
                "units of "
                "the "
                "currency "
                "e.g. "
                "pence, "
                "cents.",
                "examples": ["100000"],
                "title": "Balance",
                "type": "integer",
            },
            "billing_cycle": {
                "anyOf": [{"type": "string"}, {"type": "null"}],
                "description": "The "
                "current "
                "billing "
                "cycle, "
                "for "
                "example "
                "the "
                "current "
                "calendar "
                "month "
                "(UTC). "
                "If "
                "the "
                "billing "
                "cycle "
                "is "
                "None, "
                "the "
                "billing "
                "period "
                "will "
                "be "
                "from "
                "the "
                "contract "
                "start "
                "date.",
                "examples": [None, "12-2025"],
                "title": "Billing Cycle",
            },
            "currency": {
                "description": "The currency of the credit balance.",
                "examples": ["GBP", "EUR", "USD"],
                "title": "Currency",
                "type": "string",
            },
        },
        "required": ["currency", "balance", "billing_cycle"],
        "title": "CreditBalanceResponse",
        "type": "object",
    },
    "HTTPValidationError": {
        "properties": {
            "detail": {
                "items": {"$ref": "#/definitions/ValidationError"},
                "title": "Detail",
                "type": "array",
            }
        },
        "title": "HTTPValidationError",
        "type": "object",
    },
    "ValidationError": {
        "properties": {
            "loc": {
                "items": {"anyOf": [{"type": "string"}, {"type": "integer"}]},
                "title": "Location",
                "type": "array",
            },
            "msg": {"title": "Message", "type": "string"},
            "type": {"title": "Error Type", "type": "string"},
        },
        "required": ["loc", "msg", "type"],
        "title": "ValidationError",
        "type": "object",
    },
}

# Operations: (path, method) -> {responses, requestBody, parameters}
# Each schema has definitions attached for $ref resolution
_OPERATIONS = {
    ("/balances", "get"): {
        "parameters": {},
        "responses": {
            "200": {
                "is_error": False,
                "schema": {
                    "definitions": {
                        "BatchBalanceResponse": {
                            "properties": {
                                "balances": {
                                    "additionalProperties": {
                                        "$ref": "#/definitions/CreditBalanceResponse"
                                    },
                                    "description": "Mapping "
                                    "of "
                                    "contract "
                                    "IDs "
                                    "to "
                                    "their "
                                    "credit "
                                    "balance "
                                    "responses",
                                    "propertyNames": {"format": "uuid"},
                                    "title": "Balances",
                                    "type": "object",
                                }
                            },
                            "required": ["balances"],
                            "title": "BatchBalanceResponse",
                            "type": "object",
                        },
                        "CreditBalanceResponse": {
                            "properties": {
                                "balance": {
                                    "description": "The "
                                    "credit "
                                    "balance "
                                    "of "
                                    "the "
                                    "user, "
                                    "in "
                                    "minor "
                                    "units "
                                    "of "
                                    "the "
                                    "currency "
                                    "e.g. "
                                    "pence, "
                                    "cents.",
                                    "examples": ["100000"],
                                    "title": "Balance",
                                    "type": "integer",
                                },
                                "billing_cycle": {
                                    "anyOf": [{"type": "string"}, {"type": "null"}],
                                    "description": "The "
                                    "current "
                                    "billing "
                                    "cycle, "
                                    "for "
                                    "example "
                                    "the "
                                    "current "
                                    "calendar "
                                    "month "
                                    "(UTC). "
                                    "If "
                                    "the "
                                    "billing "
                                    "cycle "
                                    "is "
                                    "None, "
                                    "the "
                                    "billing "
                                    "period "
                                    "will "
                                    "be "
                                    "from "
                                    "the "
                                    "contract "
                                    "start "
                                    "date.",
                                    "examples": [None, "12-2025"],
                                    "title": "Billing Cycle",
                                },
                                "currency": {
                                    "description": "The "
                                    "currency "
                                    "of "
                                    "the "
                                    "credit "
                                    "balance.",
                                    "examples": ["GBP", "EUR", "USD"],
                                    "title": "Currency",
                                    "type": "string",
                                },
                            },
                            "required": ["currency", "balance", "billing_cycle"],
                            "title": "CreditBalanceResponse",
                            "type": "object",
                        },
                        "HTTPValidationError": {
                            "properties": {
                                "detail": {
                                    "items": {"$ref": "#/definitions/ValidationError"},
                                    "title": "Detail",
                                    "type": "array",
                                }
                            },
                            "title": "HTTPValidationError",
                            "type": "object",
                        },
                        "ValidationError": {
                            "properties": {
                                "loc": {
                                    "items": {
                                        "anyOf": [
                                            {"type": "string"},
                                            {"type": "integer"},
                                        ]
                                    },
                                    "title": "Location",
                                    "type": "array",
                                },
                                "msg": {"title": "Message", "type": "string"},
                                "type": {"title": "Error Type", "type": "string"},
                            },
                            "required": ["loc", "msg", "type"],
                            "title": "ValidationError",
                            "type": "object",
                        },
                    },
                    "properties": {
                        "balances": {
                            "additionalProperties": {
                                "$ref": "#/definitions/CreditBalanceResponse"
                            },
                            "description": "Mapping "
                            "of "
                            "contract "
                            "IDs "
                            "to "
                            "their "
                            "credit "
                            "balance "
                            "responses",
                            "propertyNames": {"format": "uuid"},
                            "title": "Balances",
                            "type": "object",
                        }
                    },
                    "required": ["balances"],
                    "title": "BatchBalanceResponse",
                    "type": "object",
                },
            }
        },
    },
    ("/{contract_id}/credit", "get"): {
        "parameters": {},
        "responses": {
            "200": {
                "is_error": False,
                "schema": {
                    "definitions": {
                        "BatchBalanceResponse": {
                            "properties": {
                                "balances": {
                                    "additionalProperties": {
                                        "$ref": "#/definitions/CreditBalanceResponse"
                                    },
                                    "description": "Mapping "
                                    "of "
                                    "contract "
                                    "IDs "
                                    "to "
                                    "their "
                                    "credit "
                                    "balance "
                                    "responses",
                                    "propertyNames": {"format": "uuid"},
                                    "title": "Balances",
                                    "type": "object",
                                }
                            },
                            "required": ["balances"],
                            "title": "BatchBalanceResponse",
                            "type": "object",
                        },
                        "CreditBalanceResponse": {
                            "properties": {
                                "balance": {
                                    "description": "The "
                                    "credit "
                                    "balance "
                                    "of "
                                    "the "
                                    "user, "
                                    "in "
                                    "minor "
                                    "units "
                                    "of "
                                    "the "
                                    "currency "
                                    "e.g. "
                                    "pence, "
                                    "cents.",
                                    "examples": ["100000"],
                                    "title": "Balance",
                                    "type": "integer",
                                },
                                "billing_cycle": {
                                    "anyOf": [{"type": "string"}, {"type": "null"}],
                                    "description": "The "
                                    "current "
                                    "billing "
                                    "cycle, "
                                    "for "
                                    "example "
                                    "the "
                                    "current "
                                    "calendar "
                                    "month "
                                    "(UTC). "
                                    "If "
                                    "the "
                                    "billing "
                                    "cycle "
                                    "is "
                                    "None, "
                                    "the "
                                    "billing "
                                    "period "
                                    "will "
                                    "be "
                                    "from "
                                    "the "
                                    "contract "
                                    "start "
                                    "date.",
                                    "examples": [None, "12-2025"],
                                    "title": "Billing Cycle",
                                },
                                "currency": {
                                    "description": "The "
                                    "currency "
                                    "of "
                                    "the "
                                    "credit "
                                    "balance.",
                                    "examples": ["GBP", "EUR", "USD"],
                                    "title": "Currency",
                                    "type": "string",
                                },
                            },
                            "required": ["currency", "balance", "billing_cycle"],
                            "title": "CreditBalanceResponse",
                            "type": "object",
                        },
                        "HTTPValidationError": {
                            "properties": {
                                "detail": {
                                    "items": {"$ref": "#/definitions/ValidationError"},
                                    "title": "Detail",
                                    "type": "array",
                                }
                            },
                            "title": "HTTPValidationError",
                            "type": "object",
                        },
                        "ValidationError": {
                            "properties": {
                                "loc": {
                                    "items": {
                                        "anyOf": [
                                            {"type": "string"},
                                            {"type": "integer"},
                                        ]
                                    },
                                    "title": "Location",
                                    "type": "array",
                                },
                                "msg": {"title": "Message", "type": "string"},
                                "type": {"title": "Error Type", "type": "string"},
                            },
                            "required": ["loc", "msg", "type"],
                            "title": "ValidationError",
                            "type": "object",
                        },
                    },
                    "properties": {
                        "balance": {
                            "description": "The "
                            "credit "
                            "balance "
                            "of "
                            "the "
                            "user, "
                            "in "
                            "minor "
                            "units "
                            "of "
                            "the "
                            "currency "
                            "e.g. "
                            "pence, "
                            "cents.",
                            "examples": ["100000"],
                            "title": "Balance",
                            "type": "integer",
                        },
                        "billing_cycle": {
                            "anyOf": [{"type": "string"}, {"type": "null"}],
                            "description": "The "
                            "current "
                            "billing "
                            "cycle, "
                            "for "
                            "example "
                            "the "
                            "current "
                            "calendar "
                            "month "
                            "(UTC). "
                            "If "
                            "the "
                            "billing "
                            "cycle "
                            "is "
                            "None, "
                            "the "
                            "billing "
                            "period "
                            "will "
                            "be "
                            "from "
                            "the "
                            "contract "
                            "start "
                            "date.",
                            "examples": [None, "12-2025"],
                            "title": "Billing Cycle",
                        },
                        "currency": {
                            "description": "The currency of the credit balance.",
                            "examples": ["GBP", "EUR", "USD"],
                            "title": "Currency",
                            "type": "string",
                        },
                    },
                    "required": ["currency", "balance", "billing_cycle"],
                    "title": "CreditBalanceResponse",
                    "type": "object",
                },
            },
            "422": {
                "is_error": True,
                "schema": {
                    "definitions": {
                        "BatchBalanceResponse": {
                            "properties": {
                                "balances": {
                                    "additionalProperties": {
                                        "$ref": "#/definitions/CreditBalanceResponse"
                                    },
                                    "description": "Mapping "
                                    "of "
                                    "contract "
                                    "IDs "
                                    "to "
                                    "their "
                                    "credit "
                                    "balance "
                                    "responses",
                                    "propertyNames": {"format": "uuid"},
                                    "title": "Balances",
                                    "type": "object",
                                }
                            },
                            "required": ["balances"],
                            "title": "BatchBalanceResponse",
                            "type": "object",
                        },
                        "CreditBalanceResponse": {
                            "properties": {
                                "balance": {
                                    "description": "The "
                                    "credit "
                                    "balance "
                                    "of "
                                    "the "
                                    "user, "
                                    "in "
                                    "minor "
                                    "units "
                                    "of "
                                    "the "
                                    "currency "
                                    "e.g. "
                                    "pence, "
                                    "cents.",
                                    "examples": ["100000"],
                                    "title": "Balance",
                                    "type": "integer",
                                },
                                "billing_cycle": {
                                    "anyOf": [{"type": "string"}, {"type": "null"}],
                                    "description": "The "
                                    "current "
                                    "billing "
                                    "cycle, "
                                    "for "
                                    "example "
                                    "the "
                                    "current "
                                    "calendar "
                                    "month "
                                    "(UTC). "
                                    "If "
                                    "the "
                                    "billing "
                                    "cycle "
                                    "is "
                                    "None, "
                                    "the "
                                    "billing "
                                    "period "
                                    "will "
                                    "be "
                                    "from "
                                    "the "
                                    "contract "
                                    "start "
                                    "date.",
                                    "examples": [None, "12-2025"],
                                    "title": "Billing Cycle",
                                },
                                "currency": {
                                    "description": "The "
                                    "currency "
                                    "of "
                                    "the "
                                    "credit "
                                    "balance.",
                                    "examples": ["GBP", "EUR", "USD"],
                                    "title": "Currency",
                                    "type": "string",
                                },
                            },
                            "required": ["currency", "balance", "billing_cycle"],
                            "title": "CreditBalanceResponse",
                            "type": "object",
                        },
                        "HTTPValidationError": {
                            "properties": {
                                "detail": {
                                    "items": {"$ref": "#/definitions/ValidationError"},
                                    "title": "Detail",
                                    "type": "array",
                                }
                            },
                            "title": "HTTPValidationError",
                            "type": "object",
                        },
                        "ValidationError": {
                            "properties": {
                                "loc": {
                                    "items": {
                                        "anyOf": [
                                            {"type": "string"},
                                            {"type": "integer"},
                                        ]
                                    },
                                    "title": "Location",
                                    "type": "array",
                                },
                                "msg": {"title": "Message", "type": "string"},
                                "type": {"title": "Error Type", "type": "string"},
                            },
                            "required": ["loc", "msg", "type"],
                            "title": "ValidationError",
                            "type": "object",
                        },
                    },
                    "properties": {
                        "detail": {
                            "items": {"$ref": "#/definitions/ValidationError"},
                            "title": "Detail",
                            "type": "array",
                        }
                    },
                    "title": "HTTPValidationError",
                    "type": "object",
                },
            },
        },
    },
}


def get_response_schema(path: str, method: str, status: str) -> dict:
    """
    Get response schema for given operation and status code.

    Args:
        path: Endpoint path (e.g., "/{contract_id}/")
        method: HTTP method (e.g., "get", "post")
        status: Status code (e.g., "200", "404")

    Returns:
        JSON Schema dict with definitions for $ref resolution
    """
    return _OPERATIONS[(path, method)]["responses"][status]["schema"]


def get_request_body_schema(path: str, method: str) -> dict:
    """
    Get request body schema for given operation.

    Args:
        path: Endpoint path (e.g., "/{contract_id}/search")
        method: HTTP method (e.g., "post", "put")

    Returns:
        JSON Schema dict with definitions for $ref resolution
    """
    return _OPERATIONS[(path, method)]["requestBody"]["schema"]


def get_parameter_schema(path: str, method: str, param_name: str) -> dict:
    """
    Get query parameter schema for given operation.

    Args:
        path: Endpoint path
        method: HTTP method
        param_name: Parameter name (e.g., "limit", "token")

    Returns:
        JSON Schema dict
    """
    return _OPERATIONS[(path, method)]["parameters"][param_name]["schema"]


def has_request_body(path: str, method: str) -> bool:
    """Check if operation has a request body."""
    return "requestBody" in _OPERATIONS.get((path, method), {})


def has_parameter(path: str, method: str, param_name: str) -> bool:
    """Check if operation has a specific parameter."""
    return param_name in _OPERATIONS.get((path, method), {}).get("parameters", {})


def is_error_response(path: str, method: str, status: str) -> bool:
    """Check if response is an error response (4xx/5xx)."""
    response = _OPERATIONS.get((path, method), {}).get("responses", {}).get(status, {})
    return response.get("is_error", False)


def has_response_schema(path: str, method: str, status: str) -> bool:
    """Check if operation has a response schema for given status."""
    return status in _OPERATIONS.get((path, method), {}).get("responses", {})
