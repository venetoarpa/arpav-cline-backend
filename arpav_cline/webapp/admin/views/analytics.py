import functools
from typing import (
    Any,
    Optional,
    Sequence,
    Union,
)

import anyio.to_thread
import starlette_admin
from starlette.requests import Request
from starlette_admin.contrib.sqlmodel import ModelView

from .... import db
from ....schemas.analytics import (
    ForecastCoverageDownloadRequest,
    HistoricalCoverageDownloadRequest,
    TimeSeriesDownloadRequest,
)

from ..schemas import (
    ForecastCoverageDownloadRequestRead,
    HistoricalCoverageDownloadRequestRead,
    TimeSeriesDownloadRequestRead,
)


class ForecastCoverageDownloadRequestView(ModelView):
    identity = "forecast_coverage_download_requests"
    name = "Forecast Coverage Download Request"
    label = "Forecasts"
    pk_attr = "id"

    exclude_fields_from_list = ("id",)
    exclude_fields_from_detail = ("id",)

    fields = (
        starlette_admin.IntegerField("id"),
        starlette_admin.DateTimeField("request_datetime"),
        starlette_admin.StringField("entity_name"),
        starlette_admin.BooleanField("is_public_sector"),
        starlette_admin.StringField("download_reason"),
        starlette_admin.StringField("climatological_variable"),
        starlette_admin.StringField("aggregation_period"),
        starlette_admin.StringField("measure_type"),
        starlette_admin.StringField("year_period"),
        starlette_admin.StringField("climatological_model"),
        starlette_admin.StringField("scenario"),
        starlette_admin.StringField("time_window"),
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.icon = "fa-solid fa-map"

    def can_create(self, request: Request) -> bool:
        return False

    def can_edit(self, request: Request) -> bool:
        return False

    def can_view_details(self, request: Request) -> bool:
        return False

    @staticmethod
    def _serialize_instance(instance: ForecastCoverageDownloadRequest):
        return ForecastCoverageDownloadRequestRead(**instance.model_dump())

    async def find_by_pk(
        self, request: Request, pk: Any
    ) -> ForecastCoverageDownloadRequestRead:
        db_item = await anyio.to_thread.run_sync(
            db.get_forecast_coverage_download_request, request.state.session, pk
        )
        return self._serialize_instance(db_item)

    async def find_all(
        self,
        request: Request,
        skip: int = 0,
        limit: int = 100,
        where: Union[dict[str, Any], str, None] = None,
        order_by: Optional[list[str]] = None,
    ) -> Sequence[ForecastCoverageDownloadRequestRead]:
        finder = functools.partial(
            db.collect_all_forecast_coverage_download_requests,
        )
        db_items = await anyio.to_thread.run_sync(finder, request.state.session)
        return [self._serialize_instance(ind) for ind in db_items]

    async def count(
        self,
        request: Request,
        where: Union[dict[str, Any], str, None] = None,
    ) -> int:
        finder = functools.partial(
            db.collect_all_forecast_coverage_download_requests,
        )
        found = await anyio.to_thread.run_sync(
            finder,
            request.state.session,
        )
        return len(found)


class HistoricalCoverageDownloadRequestView(ModelView):
    identity = "historical_coverage_download_requests"
    name = "Historical Coverage Download Request"
    label = "historical"
    pk_attr = "id"

    exclude_fields_from_list = ("id",)
    exclude_fields_from_detail = ("id",)

    fields = (
        starlette_admin.IntegerField("id"),
        starlette_admin.DateTimeField("request_datetime"),
        starlette_admin.StringField("entity_name"),
        starlette_admin.BooleanField("is_public_sector"),
        starlette_admin.StringField("download_reason"),
        starlette_admin.StringField("climatological_variable"),
        starlette_admin.StringField("aggregation_period"),
        starlette_admin.StringField("measure_type"),
        starlette_admin.StringField("year_period"),
        starlette_admin.StringField("decade"),
        starlette_admin.StringField("reference_period"),
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.icon = "fa-solid fa-map"

    def can_create(self, request: Request) -> bool:
        return False

    def can_edit(self, request: Request) -> bool:
        return False

    def can_view_details(self, request: Request) -> bool:
        return False

    @staticmethod
    def _serialize_instance(instance: HistoricalCoverageDownloadRequest):
        return HistoricalCoverageDownloadRequestRead(**instance.model_dump())

    async def find_by_pk(
        self, request: Request, pk: Any
    ) -> HistoricalCoverageDownloadRequestRead:
        db_item = await anyio.to_thread.run_sync(
            db.get_historical_coverage_download_request, request.state.session, pk
        )
        return self._serialize_instance(db_item)

    async def find_all(
        self,
        request: Request,
        skip: int = 0,
        limit: int = 100,
        where: Union[dict[str, Any], str, None] = None,
        order_by: Optional[list[str]] = None,
    ) -> Sequence[HistoricalCoverageDownloadRequestRead]:
        finder = functools.partial(
            db.collect_all_historical_coverage_download_requests,
        )
        db_items = await anyio.to_thread.run_sync(finder, request.state.session)
        return [self._serialize_instance(ind) for ind in db_items]

    async def count(
        self,
        request: Request,
        where: Union[dict[str, Any], str, None] = None,
    ) -> int:
        finder = functools.partial(
            db.collect_all_historical_coverage_download_requests,
        )
        found = await anyio.to_thread.run_sync(
            finder,
            request.state.session,
        )
        return len(found)


class TimeSeriesDownloadRequestView(ModelView):
    identity = "time_series_download_requests"
    name = "Time Series Download Request"
    label = "Time series"
    pk_attr = "id"

    exclude_fields_from_list = ("id",)
    exclude_fields_from_detail = ("id",)

    fields = (
        starlette_admin.IntegerField("id"),
        starlette_admin.DateTimeField("request_datetime"),
        starlette_admin.StringField("entity_name"),
        starlette_admin.BooleanField("is_public_sector"),
        starlette_admin.StringField("download_reason"),
        starlette_admin.StringField("climatological_variable"),
        starlette_admin.StringField("aggregation_period"),
        starlette_admin.StringField("measure_type"),
        starlette_admin.StringField("year_period"),
        starlette_admin.StringField("data_category"),
        starlette_admin.FloatField("longitude"),
        starlette_admin.FloatField("latitude"),
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.icon = "fa-solid fa-map"

    def can_create(self, request: Request) -> bool:
        return False

    def can_edit(self, request: Request) -> bool:
        return False

    def can_view_details(self, request: Request) -> bool:
        return False

    @staticmethod
    def _serialize_instance(instance: TimeSeriesDownloadRequest):
        return TimeSeriesDownloadRequestRead(**instance.model_dump())

    async def find_by_pk(
        self, request: Request, pk: Any
    ) -> TimeSeriesDownloadRequestRead:
        db_item = await anyio.to_thread.run_sync(
            db.get_time_series_download_request, request.state.session, pk
        )
        return self._serialize_instance(db_item)

    async def find_all(
        self,
        request: Request,
        skip: int = 0,
        limit: int = 100,
        where: Union[dict[str, Any], str, None] = None,
        order_by: Optional[list[str]] = None,
    ) -> Sequence[TimeSeriesDownloadRequestRead]:
        finder = functools.partial(
            db.collect_all_time_series_download_requests,
        )
        db_items = await anyio.to_thread.run_sync(finder, request.state.session)
        return [self._serialize_instance(ind) for ind in db_items]

    async def count(
        self,
        request: Request,
        where: Union[dict[str, Any], str, None] = None,
    ) -> int:
        finder = functools.partial(
            db.collect_all_time_series_download_requests,
        )
        found = await anyio.to_thread.run_sync(
            finder,
            request.state.session,
        )
        return len(found)
