"""Contains all the data models used in inputs/outputs"""

from .collection import Collection
from .feature_collection_order import FeatureCollectionOrder
from .feature_order import FeatureOrder
from .geojson_polygon import GeojsonPolygon
from .http_exception_response import HttpExceptionResponse
from .http_validation_error import HTTPValidationError
from .link import Link
from .method import Method
from .order import Order
from .order_download_url import OrderDownloadUrl
from .order_edit_payload import OrderEditPayload
from .order_item_download_url import OrderItemDownloadUrl
from .order_item_price import OrderItemPrice
from .order_page import OrderPage
from .order_price import OrderPrice
from .order_pricing import OrderPricing
from .order_submission_payload import OrderSubmissionPayload
from .point_geometry import PointGeometry
from .polygon import Polygon
from .polygon_1 import Polygon1
from .polygon_geometry import PolygonGeometry
from .price_information import PriceInformation
from .price_request import PriceRequest
from .primary_format import PrimaryFormat
from .reseller_feature_collection_order import ResellerFeatureCollectionOrder
from .reseller_order_price import ResellerOrderPrice
from .reseller_price_request import ResellerPriceRequest
from .reseller_submission_order_payload import ResellerSubmissionOrderPayload
from .response_context import ResponseContext
from .satvu_filter import SatvuFilter
from .search_request import SearchRequest
from .stac_metadata import StacMetadata
from .stac_properties_v4 import StacPropertiesV4
from .stac_properties_v7 import StacPropertiesV7
from .stac_properties_v9 import StacPropertiesV9
from .validation_error import ValidationError

__all__ = (
    "Collection",
    "FeatureCollectionOrder",
    "FeatureOrder",
    "GeojsonPolygon",
    "HttpExceptionResponse",
    "HTTPValidationError",
    "Link",
    "Method",
    "Order",
    "OrderDownloadUrl",
    "OrderEditPayload",
    "OrderItemDownloadUrl",
    "OrderItemPrice",
    "OrderPage",
    "OrderPrice",
    "OrderPricing",
    "OrderSubmissionPayload",
    "PointGeometry",
    "Polygon",
    "Polygon1",
    "PolygonGeometry",
    "PriceInformation",
    "PriceRequest",
    "PrimaryFormat",
    "ResellerFeatureCollectionOrder",
    "ResellerOrderPrice",
    "ResellerPriceRequest",
    "ResellerSubmissionOrderPayload",
    "ResponseContext",
    "SatvuFilter",
    "SearchRequest",
    "StacMetadata",
    "StacPropertiesV4",
    "StacPropertiesV7",
    "StacPropertiesV9",
    "ValidationError",
)

# Ensure all Pydantic models have forward refs rebuilt
import inspect
import sys

from pydantic import BaseModel

_current_module = sys.modules[__name__]

for _obj in list(_current_module.__dict__.values()):
    if inspect.isclass(_obj) and issubclass(_obj, BaseModel) and _obj is not BaseModel:
        _obj.model_rebuild()
