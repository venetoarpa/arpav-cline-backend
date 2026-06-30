import logging
from typing import Any

import anyio.to_thread
import starlette_admin
from starlette.requests import Request
from starlette_admin import RequestAction

from ... import db

logger = logging.getLogger(__name__)


class RelatedForecastModelGroupField(starlette_admin.EnumField):
    def __post_init__(self) -> None:
        self.choices_loader = RelatedForecastModelGroupField.choices_loader
        super().__post_init__()

    # def _get_label(self, value: int, request: Request) -> str:
    #     session = request.state.session
    #     db_forecast_model_group = db.get_forecast_model_group(session, value)
    #     return db_forecast_model_group.name
    #
    # async def serialize_value(
    #     self,
    #     request: Request,
    #     value: int,
    #     action: starlette_admin.RequestAction,
    # ) -> Any:
    #     return self._get_label(value, request)

    @staticmethod
    def choices_loader(request: Request):
        all_forecast_model_groups = db.collect_all_forecast_model_groups(
            request.state.session
        )
        return [(fmg.id, fmg.name) for fmg in all_forecast_model_groups]


class RelatedForecastYearPeriodGroupField(starlette_admin.EnumField):
    def __post_init__(self) -> None:
        self.choices_loader = RelatedForecastYearPeriodGroupField.choices_loader
        super().__post_init__()

    @staticmethod
    def choices_loader(request: Request):
        all_year_period_groups = db.collect_all_forecast_year_period_groups(
            request.state.session
        )
        return [(ypg.id, ypg.name) for ypg in all_year_period_groups]


class RelatedHistoricalYearPeriodGroupField(starlette_admin.EnumField):
    def __post_init__(self) -> None:
        self.choices_loader = RelatedHistoricalYearPeriodGroupField.choices_loader
        super().__post_init__()

    # def _get_label(self, value: int, request: Request) -> str:
    #     session = request.state.session
    #     db_year_period_group = db.get_historical_year_period_group(session, value)
    #     return db_year_period_group.name
    #
    # async def serialize_value(
    #     self,
    #     request: Request,
    #     value: int,
    #     action: starlette_admin.RequestAction,
    # ) -> Any:
    #     return self._get_label(value, request)

    @staticmethod
    def choices_loader(request: Request):
        all_year_period_groups = db.collect_all_historical_year_period_groups(
            request.state.session
        )
        return [(ypg.id, ypg.name) for ypg in all_year_period_groups]


class RelatedForecastModelField(starlette_admin.EnumField):
    def __post_init__(self) -> None:
        self.choices_loader = RelatedForecastModelField.choices_loader
        super().__post_init__()

    @staticmethod
    def choices_loader(request: Request):
        all_forecast_models = db.collect_all_forecast_models(request.state.session)
        return [(fm.id, fm.name) for fm in all_forecast_models]


class RelatedForecastModelsField(starlette_admin.EnumField):
    def __post_init__(self) -> None:
        self.choices_loader = RelatedForecastModelsField.choices_loader
        super().__post_init__()

    def _get_label(self, value: int, request: Request) -> str:
        result = None
        for v, label in self._get_choices(request):
            if value == v:
                result = label
                break
        return result

    async def serialize_value(
        self, request: Request, value: Any, action: starlette_admin.RequestAction
    ) -> Any:
        labels = [
            (
                self._get_label(v, request)
                if action != starlette_admin.RequestAction.EDIT
                else v
            )
            for v in (value if self.multiple else [value])
        ]
        return labels if self.multiple else labels[0]

    @staticmethod
    def choices_loader(request: Request):
        all_forecast_models = db.collect_all_forecast_models(request.state.session)
        result = [(fm.id, fm.name) for fm in all_forecast_models]
        return result


class RelatedForecastTimeWindowField(starlette_admin.EnumField):
    def __post_init__(self) -> None:
        self.choices_loader = RelatedForecastTimeWindowField.choices_loader
        super().__post_init__()

    async def serialize_value(
        self, request: Request, value: Any, action: starlette_admin.RequestAction
    ) -> Any:
        session = request.state.session
        if self.multiple:
            instances = [
                await anyio.to_thread.run_sync(db.get_forecast_time_window, session, v)
                for v in value
            ]
            result = [self._get_label(i.id, request) for i in instances]
        else:
            instance = await anyio.to_thread.run_sync(
                db.get_forecast_time_window, session, value
            )
            result = self._get_label(instance.id, request)
        return result

    @staticmethod
    def choices_loader(request: Request):
        all_forecast_time_windows = db.collect_all_forecast_time_windows(
            request.state.session
        )
        return [(tw.id, tw.name) for tw in all_forecast_time_windows]


class RelatedObservationSeriesConfigurationField(starlette_admin.EnumField):
    def __post_init__(self) -> None:
        self.choices_loader = RelatedObservationSeriesConfigurationField.choices_loader
        super().__post_init__()

    @staticmethod
    def choices_loader(request: Request):
        all_obs_series_confs = db.collect_all_observation_series_configurations(
            request.state.session
        )
        return [(osc.id, osc.identifier) for osc in all_obs_series_confs]


class RelatedObservationStationField(starlette_admin.EnumField):
    def __post_init__(self) -> None:
        self.search_builder_type = "eq_only"
        self.choices_loader = RelatedObservationStationField.choices_loader
        super().__post_init__()

    def additional_js_links(self, request: Request, action: RequestAction) -> list[str]:
        if action == RequestAction.LIST:
            return [str(request.url_for("admin:statics", path="eq-only-conditions.js"))]
        return []

    async def serialize_value(
        self, request: Request, value: Any, action: starlette_admin.RequestAction
    ) -> Any:
        session = request.state.session
        if self.multiple:
            instances = [
                await anyio.to_thread.run_sync(db.get_observation_station, session, v)
                for v in value
            ]
            result = [self._get_label(i.id, request) for i in instances]
        else:
            instance = await anyio.to_thread.run_sync(
                db.get_observation_station, session, value
            )
            result = self._get_label(instance.id, request)
        return result

    @staticmethod
    def choices_loader(request: Request) -> list[tuple[int, str]]:
        all_stations = db.collect_all_observation_stations(request.state.session)
        return [(s.id, s.name) for s in all_stations]


class RelatedSpatialRegionField(starlette_admin.EnumField):
    def __post_init__(self) -> None:
        self.choices_loader = RelatedSpatialRegionField.choices_loader
        super().__post_init__()

    # async def serialize_value(
    #     self, request: Request, value: Any, action: starlette_admin.RequestAction
    # ) -> Any:
    #     session = request.state.session
    #     if self.multiple:
    #         instances = [
    #             await anyio.to_thread.run_sync(db.get_spatial_region, session, v)
    #             for v in value
    #         ]
    #         result = [self._get_label(i.id, request) for i in instances]
    #     else:
    #         instance = await anyio.to_thread.run_sync(
    #             db.get_spatial_region, session, value
    #         )
    #         result = self._get_label(instance.id, request)
    #     return result

    @staticmethod
    def choices_loader(request: Request):
        all_spatial_regions = db.collect_all_spatial_regions(request.state.session)
        return [(sr.id, sr.name) for sr in all_spatial_regions]


class RelatedClimaticIndicatorField(starlette_admin.EnumField):
    """Custom field to show a 1:m relationship.

    This somewhat abuses the default way to represent relationships in starlete_admin.
    However, it provides more control over presentation of data.

    Things to consider here are:

    - overriding `__post_init__()` as a way to define `choices_loader` together with
    the custom field - the alternative would be to write the choices loader as a
    standalone function and then use it in the field initializer, which would
    put them in different files.

    - overriding `get_label()` as way to use the climatic_identifier.identifier field
    as a friendlier way to refer to the instance in forms

    """

    def __post_init__(self) -> None:
        self.search_builder_type = "eq_only"
        self.choices_loader = RelatedClimaticIndicatorField.choices_loader
        super().__post_init__()

    # async def serialize_value(
    #     self, request: Request, value: Any, action: starlette_admin.RequestAction
    # ) -> Any:
    #     logger.debug(f"relatedclimaticindicatorfield.serialize_value - value: {value} - action: {action}")
    #     session = request.state.session
    #     if self.multiple:
    #         instances = [
    #             await anyio.to_thread.run_sync(db.get_climatic_indicator, session, v)
    #             for v in value
    #         ]
    #         result = [self._get_label(i.id, request) for i in instances]
    #     else:
    #         instance = await anyio.to_thread.run_sync(
    #             db.get_climatic_indicator, session, value
    #         )
    #         result = self._get_label(instance.id, request)
    #     logger.debug(f"inside relatedclimaticindicatorfield.serialize_value - result: {result}")
    #     return result

    @staticmethod
    def choices_loader(request: Request):
        all_climatic_indicators = db.collect_all_climatic_indicators(
            request.state.session
        )
        return [(ci.id, ci.identifier) for ci in all_climatic_indicators]
