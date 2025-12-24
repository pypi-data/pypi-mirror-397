"""Contains all the data models used in inputs/outputs"""

from .and_or_expression import AndOrExpression
from .and_or_expression_op import AndOrExpressionOp
from .api_error import ApiError
from .arithmetic_expression import ArithmeticExpression
from .arithmetic_expression_op import ArithmeticExpressionOp
from .asset import Asset
from .asset_bands import AssetBands
from .asset_bands_nodata_type_1 import AssetBandsNodataType1
from .asset_bands_statistics import AssetBandsStatistics
from .bbox_literal import BboxLiteral
from .binary_comparison_predicate import BinaryComparisonPredicate
from .binary_comparison_predicate_op import BinaryComparisonPredicateOp
from .catalog import Catalog
from .collection import Collection
from .collections import Collections
from .conformance import Conformance
from .conformance_response_429 import ConformanceResponse429
from .cql_2_queryables_schema import Cql2QueryablesSchema
from .data_type_of_the_band import DataTypeOfTheBand
from .date_instant import DateInstant
from .error import Error
from .extent import Extent
from .feature import Feature
from .feature_collection import FeatureCollection
from .feature_properties import FeatureProperties
from .geo_json_geometry_collection import GeoJSONGeometryCollection
from .geo_json_geometry_collection_type import GeoJSONGeometryCollectionType
from .geo_json_line_string import GeoJSONLineString
from .geo_json_line_string_type import GeoJSONLineStringType
from .geo_json_multi_line_string import GeoJSONMultiLineString
from .geo_json_multi_line_string_type import GeoJSONMultiLineStringType
from .geo_json_multi_point import GeoJSONMultiPoint
from .geo_json_multi_point_type import GeoJSONMultiPointType
from .geo_json_multi_polygon import GeoJSONMultiPolygon
from .geo_json_multi_polygon_type import GeoJSONMultiPolygonType
from .geo_json_point import GeoJSONPoint
from .geo_json_point_type import GeoJSONPointType
from .geo_json_polygon import GeoJSONPolygon
from .geo_json_polygon_type import GeoJSONPolygonType
from .geojson_crs import GeojsonCRS
from .geojson_geometry import GeojsonGeometry
from .get_collection_response_429 import GetCollectionResponse429
from .get_collections_response_429 import GetCollectionsResponse429
from .get_item_collection_response_429 import GetItemCollectionResponse429
from .get_item_response_429 import GetItemResponse429
from .get_search_response_429 import GetSearchResponse429
from .http_error import HttpError
from .is_between_predicate import IsBetweenPredicate
from .is_between_predicate_op import IsBetweenPredicateOp
from .is_in_list_predicate import IsInListPredicate
from .is_in_list_predicate_op import IsInListPredicateOp
from .is_like_predicate import IsLikePredicate
from .is_like_predicate_op import IsLikePredicateOp
from .is_null_predicate import IsNullPredicate
from .is_null_predicate_op import IsNullPredicateOp
from .landing_page_response_429 import LandingPageResponse429
from .link import Link
from .not_expression import NotExpression
from .not_expression_op import NotExpressionOp
from .pixel_sampling_in_the_band import PixelSamplingInTheBand
from .post_search_input import PostSearchInput
from .post_search_response_429 import PostSearchResponse429
from .property_ref import PropertyRef
from .queryable_property import QueryableProperty
from .queryables_response_429 import QueryablesResponse429
from .search_response import SearchResponse
from .sort_by_element import SortByElement
from .spatial_extent import SpatialExtent
from .stac_geometry import StacGeometry
from .temporal_extent import TemporalExtent
from .timestamp_instant import TimestampInstant

__all__ = (
    "AndOrExpression",
    "AndOrExpressionOp",
    "ApiError",
    "ArithmeticExpression",
    "ArithmeticExpressionOp",
    "Asset",
    "AssetBands",
    "AssetBandsNodataType1",
    "AssetBandsStatistics",
    "BboxLiteral",
    "BinaryComparisonPredicate",
    "BinaryComparisonPredicateOp",
    "Catalog",
    "Collection",
    "Collections",
    "Conformance",
    "ConformanceResponse429",
    "Cql2QueryablesSchema",
    "DataTypeOfTheBand",
    "DateInstant",
    "Error",
    "Extent",
    "Feature",
    "FeatureCollection",
    "FeatureProperties",
    "GeojsonCRS",
    "GeojsonGeometry",
    "GeoJSONGeometryCollection",
    "GeoJSONGeometryCollectionType",
    "GeoJSONLineString",
    "GeoJSONLineStringType",
    "GeoJSONMultiLineString",
    "GeoJSONMultiLineStringType",
    "GeoJSONMultiPoint",
    "GeoJSONMultiPointType",
    "GeoJSONMultiPolygon",
    "GeoJSONMultiPolygonType",
    "GeoJSONPoint",
    "GeoJSONPointType",
    "GeoJSONPolygon",
    "GeoJSONPolygonType",
    "GetCollectionResponse429",
    "GetCollectionsResponse429",
    "GetItemCollectionResponse429",
    "GetItemResponse429",
    "GetSearchResponse429",
    "HttpError",
    "IsBetweenPredicate",
    "IsBetweenPredicateOp",
    "IsInListPredicate",
    "IsInListPredicateOp",
    "IsLikePredicate",
    "IsLikePredicateOp",
    "IsNullPredicate",
    "IsNullPredicateOp",
    "LandingPageResponse429",
    "Link",
    "NotExpression",
    "NotExpressionOp",
    "PixelSamplingInTheBand",
    "PostSearchInput",
    "PostSearchResponse429",
    "PropertyRef",
    "QueryableProperty",
    "QueryablesResponse429",
    "SearchResponse",
    "SortByElement",
    "SpatialExtent",
    "StacGeometry",
    "TemporalExtent",
    "TimestampInstant",
)

# Ensure all Pydantic models have forward refs rebuilt
import inspect
import sys

from pydantic import BaseModel

_current_module = sys.modules[__name__]

for _obj in list(_current_module.__dict__.values()):
    if inspect.isclass(_obj) and issubclass(_obj, BaseModel) and _obj is not BaseModel:
        _obj.model_rebuild()
