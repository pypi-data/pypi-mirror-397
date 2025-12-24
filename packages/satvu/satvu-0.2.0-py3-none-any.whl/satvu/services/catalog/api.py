from collections.abc import Callable, Generator
from typing import Union
from uuid import UUID

from satvu.core import SDKClient
from satvu.http import HttpClient
from satvu.services.catalog.models.catalog import Catalog
from satvu.services.catalog.models.collection import Collection
from satvu.services.catalog.models.collections import Collections
from satvu.services.catalog.models.conformance import Conformance
from satvu.services.catalog.models.cql_2_queryables_schema import Cql2QueryablesSchema
from satvu.services.catalog.models.feature import Feature
from satvu.services.catalog.models.feature_collection import FeatureCollection
from satvu.services.catalog.models.geo_json_geometry_collection import (
    GeoJSONGeometryCollection,
)
from satvu.services.catalog.models.geo_json_line_string import GeoJSONLineString
from satvu.services.catalog.models.geo_json_multi_line_string import (
    GeoJSONMultiLineString,
)
from satvu.services.catalog.models.geo_json_multi_point import GeoJSONMultiPoint
from satvu.services.catalog.models.geo_json_multi_polygon import GeoJSONMultiPolygon
from satvu.services.catalog.models.geo_json_point import GeoJSONPoint
from satvu.services.catalog.models.geo_json_polygon import GeoJSONPolygon
from satvu.services.catalog.models.post_search_input import PostSearchInput
from satvu.services.catalog.models.search_response import SearchResponse
from satvu.shared.parsing import parse_response


class CatalogService(SDKClient):
    base_path = "/catalog/v1"

    def __init__(
        self,
        env: str | None,
        get_token: Callable[[], str],
        http_client: HttpClient | None = None,
        timeout: int = 30,
        max_retry_attempts: int = 5,
        max_retry_after_seconds: float = 300.0,
    ):
        super().__init__(
            env=env,
            get_token=get_token,
            http_client=http_client,
            timeout=timeout,
            max_retry_attempts=max_retry_attempts,
            max_retry_after_seconds=max_retry_after_seconds,
        )

    def landing_page(
        self,
        contract_id: UUID,
        timeout: int | None = None,
    ) -> Catalog:
        """
        Landing Page

        Landing page of the API. Entrypoint to which user can access product specifications, product
        applications and API documentation.

        Args:
            contract_id (UUID): SatVu Contract ID
            timeout: Optional request timeout in seconds. Overrides the instance timeout if
                provided.

        Returns:
            Catalog
        """

        result = self.make_request(
            method="get",
            url=f"/{contract_id}/",
            timeout=timeout,
        )

        # Raise HttpError for failed requests (network errors, 4xx, 5xx, etc.)
        if result.is_err():
            raise result.error()

        response = result.unwrap()

        if response.status_code == 200:
            return parse_response(response.json().unwrap(), Catalog)
        return response.json().unwrap()

    def conformance(
        self,
        contract_id: UUID,
        timeout: int | None = None,
    ) -> Conformance:
        """
        Conformance

        List of implemented conformance classes

        Args:
            contract_id (UUID): SatVu Contract ID
            timeout: Optional request timeout in seconds. Overrides the instance timeout if
                provided.

        Returns:
            Conformance
        """

        result = self.make_request(
            method="get",
            url=f"/{contract_id}/conformance",
            timeout=timeout,
        )

        # Raise HttpError for failed requests (network errors, 4xx, 5xx, etc.)
        if result.is_err():
            raise result.error()

        response = result.unwrap()

        if response.status_code == 200:
            return parse_response(response.json().unwrap(), Conformance)
        return response.json().unwrap()

    def queryables(
        self,
        contract_id: UUID,
        timeout: int | None = None,
    ) -> Cql2QueryablesSchema:
        """
        Queryables

        List of queryables available for CQL2 filtering

        Args:
            contract_id (UUID): SatVu Contract ID
            timeout: Optional request timeout in seconds. Overrides the instance timeout if
                provided.

        Returns:
            Cql2QueryablesSchema
        """

        result = self.make_request(
            method="get",
            url=f"/{contract_id}/queryables",
            timeout=timeout,
        )

        # Raise HttpError for failed requests (network errors, 4xx, 5xx, etc.)
        if result.is_err():
            raise result.error()

        response = result.unwrap()

        if response.status_code == 200:
            return parse_response(response.json().unwrap(), Cql2QueryablesSchema)
        return response.json().unwrap()

    def get_search(
        self,
        contract_id: UUID,
        bbox: Union[None, list[float]] = None,
        collections: Union[None, list[str]] = None,
        datetime_: None | str = None,
        filter_: Union[None, dict] = None,
        ids: Union[None, list[str]] = None,
        intersects: Union[
            None,
            Union[
                "GeoJSONGeometryCollection",
                "GeoJSONLineString",
                "GeoJSONMultiLineString",
                "GeoJSONMultiPoint",
                "GeoJSONMultiPolygon",
                "GeoJSONPoint",
                "GeoJSONPolygon",
            ],
        ] = None,
        limit: int | None = None,
        sortby: Union[None, list[str]] = None,
        token: Union[None, str] = None,
        timeout: int | None = None,
    ) -> FeatureCollection:
        """
        Search

        Perform a search on the Catalog with your desired filters. Results will be returned as a Feature
        Collection. Both GET and POST methods are supported for this request.

        Args:
            contract_id (UUID): SatVu Contract ID
            bbox (Union[None, list[float]]): Comma separated list of floats representing a bounding
                box. Only features that have a geometry that intersects the bounding box are selected.
                Example: -90,-45,90,45.
            collections (Union[None, list[str]]): Comma separated list of Collection IDs to include in
                the search for items. Only Item objects in one of the provided collections will be
                searched. Example: collection1,collection2.
            datetime_ (None | str): Single date+time, or a range ('/') separator, formatted to RFC3339
                section 5.6. Use double dots for open ranges. Example: 1985-04-12T23:20:50.52Z/...
            filter_ (Union[None, dict]): Filters using Common Query Language (CQL2).
            ids (Union[None, list[str]]): Comma separated list of Item IDs to return. Example:
                item1,item2.
            intersects (Union[None, Union['GeoJSONGeometryCollection', 'GeoJSONLineString',
                'GeoJSONMultiLineString', 'GeoJSONMultiPoint', 'GeoJSONMultiPolygon', 'GeoJSONPoint',
                'GeoJSONPolygon']]): Search for items by performing intersection between their geometry
                and a provided GeoJSON geometry.
            limit (int | None): The maximum number of results to return per page. Example: 10.
            sortby (Union[None, list[str]]): An array of property names, prefixed by either '+' for
                ascending or '-' for descending. If no prefix is provided, '-' is assumed.
            token (Union[None, str]): The pagination token.
            timeout: Optional request timeout in seconds. Overrides the instance timeout if
                provided.

        Returns:
            FeatureCollection
        """

        params = {
            "bbox": bbox,
            "collections": collections,
            "datetime": datetime_,
            "filter": filter_,
            "ids": ids,
            "intersects": intersects,
            "limit": limit,
            "sortby": sortby,
            "token": token,
        }

        result = self.make_request(
            method="get",
            url=f"/{contract_id}/search",
            params=params,
            timeout=timeout,
        )

        # Raise HttpError for failed requests (network errors, 4xx, 5xx, etc.)
        if result.is_err():
            raise result.error()

        response = result.unwrap()

        if response.status_code == 200:
            return parse_response(response.json().unwrap(), FeatureCollection)
        return response.json().unwrap()

    def get_search_iter(
        self,
        contract_id: UUID,
        bbox: Union[None, list[float]] = None,
        collections: Union[None, list[str]] = None,
        datetime_: None | str = None,
        filter_: Union[None, dict] = None,
        ids: Union[None, list[str]] = None,
        intersects: Union[
            None,
            Union[
                "GeoJSONGeometryCollection",
                "GeoJSONLineString",
                "GeoJSONMultiLineString",
                "GeoJSONMultiPoint",
                "GeoJSONMultiPolygon",
                "GeoJSONPoint",
                "GeoJSONPolygon",
            ],
        ] = None,
        limit: int | None = None,
        sortby: Union[None, list[str]] = None,
        max_pages: int | None = None,
    ) -> Generator[FeatureCollection, None, None]:
        """
        Search (Paginated Iterator)

        Automatically handles pagination by following STAC links.

        Args:
            contract_id (UUID): SatVu Contract ID
            bbox (Union[None, list[float]]): Comma separated list of floats representing a bounding
            box. Only features that have a geometry that intersects the bounding box are selected.
            Example: -90,-45,90,45.
            collections (Union[None, list[str]]): Comma separated list of Collection IDs to include in
            the search for items. Only Item objects in one of the provided collections will be
            searched. Example: collection1,collection2.
            datetime_ (None | str): Single date+time, or a range ('/') separator, formatted to RFC3339
            section 5.6. Use double dots for open ranges. Example: 1985-04-12T23:20:50.52Z/...
            filter_ (Union[None, dict]): Filters using Common Query Language (CQL2).
            ids (Union[None, list[str]]): Comma separated list of Item IDs to return. Example:
            item1,item2.
            intersects (Union[None, Union['GeoJSONGeometryCollection', 'GeoJSONLineString',
            'GeoJSONMultiLineString', 'GeoJSONMultiPoint', 'GeoJSONMultiPolygon', 'GeoJSONPoint',
            'GeoJSONPolygon']]): Search for items by performing intersection between their geometry
            and a provided GeoJSON geometry.
            limit (int | None): The maximum number of results to return per page. Example: 10.
            sortby (Union[None, list[str]]): An array of property names, prefixed by either '+' for
            ascending or '-' for descending. If no prefix is provided, '-' is assumed.
            max_pages: Stop after fetching this many pages (default: unlimited)

        Yields:
            Response pages from paginated results

        Example:
            ```python
            for page in sdk.catalog.get_search_iter(
                contract_id=...,
                max_pages=10
            ):
                for item in page.features:
                    print(item)
            ```
        """
        token = None
        page_count = 0

        while True:
            if max_pages and page_count >= max_pages:
                break

            response = self.get_search(
                contract_id=contract_id,
                bbox=bbox,
                collections=collections,
                datetime_=datetime_,
                filter_=filter_,
                ids=ids,
                intersects=intersects,
                limit=limit,
                sortby=sortby,
                token=token,
            )
            page_count += 1

            yield response

            token = self.extract_next_token(response)
            if not token:
                break

    def post_search(
        self,
        body: Union[None, PostSearchInput],
        contract_id: UUID,
        timeout: int | None = None,
    ) -> FeatureCollection:
        """
        Search

        Perform a search on the Catalog with your desired filters. Results will be returned as a Feature
        Collection. Both GET and POST methods are supported for this request.

        Args:
            contract_id (UUID): SatVu Contract ID
            body (Union[None, PostSearchInput]):
            timeout: Optional request timeout in seconds. Overrides the instance timeout if
                provided.

        Returns:
            FeatureCollection
        """

        json_body = body.model_dump(by_alias=True, mode="json") if body else None

        result = self.make_request(
            method="post",
            url=f"/{contract_id}/search",
            json=json_body,
            timeout=timeout,
        )

        # Raise HttpError for failed requests (network errors, 4xx, 5xx, etc.)
        if result.is_err():
            raise result.error()

        response = result.unwrap()

        if response.status_code == 200:
            return parse_response(response.json().unwrap(), FeatureCollection)
        return response.json().unwrap()

    def post_search_iter(
        self,
        body: Union[None, PostSearchInput],
        contract_id: UUID,
        max_pages: int | None = None,
    ) -> Generator[FeatureCollection, None, None]:
        """
        Search (Paginated Iterator)

        Automatically handles pagination by following STAC links.

        Args:
            body (Union[None, PostSearchInput]):
            contract_id (UUID): SatVu Contract ID
            max_pages: Stop after fetching this many pages (default: unlimited)

        Yields:
            Response pages from paginated results

        Example:
            ```python
            for page in sdk.catalog.post_search_iter(
                body=...,
                contract_id=...,
                max_pages=10
            ):
                for item in page.features:
                    print(item)
            ```
        """
        token = None
        page_count = 0

        while True:
            if max_pages and page_count >= max_pages:
                break

            body_with_token = body.model_copy(update={"token": token}) if body else None
            response = self.post_search(
                body=body_with_token,
                contract_id=contract_id,
            )
            page_count += 1

            yield response

            token = self.extract_next_token(response)
            if not token:
                break

    def get_collections(
        self,
        contract_id: UUID,
        timeout: int | None = None,
    ) -> Collections:
        """
        Get Collections

        List STAC Collections available within the catalog.

        Args:
            contract_id (UUID): SatVu Contract ID
            timeout: Optional request timeout in seconds. Overrides the instance timeout if
                provided.

        Returns:
            Collections
        """

        result = self.make_request(
            method="get",
            url=f"/{contract_id}/collections",
            timeout=timeout,
        )

        # Raise HttpError for failed requests (network errors, 4xx, 5xx, etc.)
        if result.is_err():
            raise result.error()

        response = result.unwrap()

        if response.status_code == 200:
            return parse_response(response.json().unwrap(), Collections)
        return response.json().unwrap()

    def get_collection(
        self,
        contract_id: UUID,
        collection_id: str,
        timeout: int | None = None,
    ) -> Collection:
        """
        Get Collection

        Retrieves the generic metadata and attributes associated with a given Collection ID within the
        catalog. To see all available Collections, please refer to GET /collections.

        Args:
            contract_id (UUID): SatVu Contract ID
            collection_id (str): Collection ID. Example: collection.
            timeout: Optional request timeout in seconds. Overrides the instance timeout if
                provided.

        Returns:
            Collection
        """

        result = self.make_request(
            method="get",
            url=f"/{contract_id}/collections/{collection_id}",
            timeout=timeout,
        )

        # Raise HttpError for failed requests (network errors, 4xx, 5xx, etc.)
        if result.is_err():
            raise result.error()

        response = result.unwrap()

        if response.status_code == 200:
            return parse_response(response.json().unwrap(), Collection)
        return response.json().unwrap()

    def get_item_collection(
        self,
        contract_id: UUID,
        collection_id: str,
        timeout: int | None = None,
    ) -> SearchResponse:
        """
        Get Item Collection

        Retrieves the entire dataset, represented as a Feature Collection, corresponding to a specified
        Collection ID.

        Args:
            contract_id (UUID): SatVu Contract ID
            collection_id (str): Collection ID. Example: collection.
            timeout: Optional request timeout in seconds. Overrides the instance timeout if
                provided.

        Returns:
            SearchResponse
        """

        result = self.make_request(
            method="get",
            url=f"/{contract_id}/collections/{collection_id}/items",
            timeout=timeout,
        )

        # Raise HttpError for failed requests (network errors, 4xx, 5xx, etc.)
        if result.is_err():
            raise result.error()

        response = result.unwrap()

        if response.status_code == 200:
            return parse_response(response.json().unwrap(), SearchResponse)
        return response.json().unwrap()

    def get_item(
        self,
        contract_id: UUID,
        collection_id: str,
        item_id: str,
        timeout: int | None = None,
    ) -> Feature:
        """
        Get Item

        Retrieves a specified imagery item from a Collection within the Catalog. The item will be
        represented as a Feature dataset.

        Args:
            contract_id (UUID): SatVu Contract ID
            collection_id (str): Collection ID. Example: collection.
            item_id (str): Item ID. Example: item.
            timeout: Optional request timeout in seconds. Overrides the instance timeout if
                provided.

        Returns:
            Feature
        """

        result = self.make_request(
            method="get",
            url=f"/{contract_id}/collections/{collection_id}/{item_id}",
            timeout=timeout,
        )

        # Raise HttpError for failed requests (network errors, 4xx, 5xx, etc.)
        if result.is_err():
            raise result.error()

        response = result.unwrap()

        if response.status_code == 200:
            return parse_response(response.json().unwrap(), Feature)
        return response.json().unwrap()
