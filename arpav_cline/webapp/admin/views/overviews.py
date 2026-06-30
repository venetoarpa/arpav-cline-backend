import functools
from typing import (
    Any,
    Optional,
    Sequence,
    Union,
)

import anyio
import starlette_admin
from starlette.requests import Request
from starlette_admin.contrib.sqlmodel import ModelView

from .... import db
from ....schemas import (
    overviews,
    static,
)
from .. import fields
from .. import schemas as read_schemas

_thredds_url_pattern_help_text = (
    "Path pattern to the dataset's URL in THREDDS. This can be "
    "templated with the name of any configuration parameter that belongs "
    "to the coverage. This can also be given a shell-like pattern, which "
    "can be useful when the dataset filename differs by additional "
    "characters than just those that are used for configuration parameters. "
    "Example: 'cline_yr/TDd_{historical_year_period}_1992-202[34]_py85.nc' "
    "- this example features the '{historical_year_period}' template, which "
    "gets replaced by the concrete value of the parameter, and it also "
    "features the shell-like style expressed in '202[34]', which means "
    "to look for files that have either '2023' or '2024' in that "
    "part of their name."
)


class ObservationOverviewSeriesConfigurationView(ModelView):
    identity = "observation_overview_series_configurations"
    name = "Observation Overview Series Configuration"
    label = "Observations"
    pk_attr = "id"

    exclude_fields_from_list = (
        "id",
        "netcdf_main_dataset_name",
        "thredds_url_pattern",
    )
    exclude_fields_from_detail = ("id",)
    exclude_fields_from_edit = ("identifier",)
    exclude_fields_from_create = ("identifier",)
    searchable_fields = ("climatic_indicator",)
    search_builder = False

    fields = (
        starlette_admin.IntegerField("id"),
        starlette_admin.StringField("identifier", read_only=True),
        starlette_admin.StringField(
            "netcdf_main_dataset_name",
            required=True,
            help_text=(
                "Name of the main variable inside this dataset's NetCDF file. This can "
                "be a templated value, such as '{historical_year_period}_avg'."
            ),
        ),
        starlette_admin.StringField(
            "thredds_url_pattern",
            required=True,
            help_text=_thredds_url_pattern_help_text,
        ),
        fields.RelatedClimaticIndicatorField(
            "climatic_indicator",
            help_text="climatic indicator",
            required=True,
        ),
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.icon = "fa-solid fa-map"

    @staticmethod
    def _serialize_instance(instance: overviews.ForecastOverviewSeriesConfiguration):
        return read_schemas.ObservationOverviewSeriesConfigurationRead(
            **instance.model_dump(
                exclude={
                    "climatic_indicator",
                }
            ),
            climatic_indicator=instance.climatic_indicator_id,
        )

    async def create(self, request: Request, data: dict[str, Any]) -> Any:
        try:
            data = await self._arrange_data(request, data)
            await self.validate(request, data)
            overview_series_configuration_create = (
                overviews.ObservationOverviewSeriesConfigurationCreate(
                    netcdf_main_dataset_name=data["netcdf_main_dataset_name"],
                    thredds_url_pattern=data["thredds_url_pattern"],
                    climatic_indicator_id=data["climatic_indicator"],
                )
            )
            db_overview_series_configuration = await anyio.to_thread.run_sync(
                db.create_observation_overview_series_configuration,
                request.state.session,
                overview_series_configuration_create,
            )
            return self._serialize_instance(db_overview_series_configuration)
        except Exception as e:
            return self.handle_exception(e)

    async def edit(self, request: Request, pk: Any, data: dict[str, Any]) -> Any:
        try:
            data = await self._arrange_data(request, data, True)
            await self.validate(request, data)
            overview_series_configuration_update = (
                overviews.ObservationOverviewSeriesConfigurationUpdate(
                    netcdf_main_dataset_name=data["netcdf_main_dataset_name"],
                    thredds_url_pattern=data["thredds_url_pattern"],
                    climatic_indicator_id=data["climatic_indicator"],
                )
            )
            db_overview_series_configuration = await anyio.to_thread.run_sync(
                db.get_observation_overview_series_configuration,
                request.state.session,
                pk,
            )
            db_overview_series_configuration = await anyio.to_thread.run_sync(
                db.update_observation_overview_series_configuration,
                request.state.session,
                db_overview_series_configuration,
                overview_series_configuration_update,
            )
            return self._serialize_instance(db_overview_series_configuration)
        except Exception as e:
            return self.handle_exception(e)

    async def find_by_pk(
        self, request: Request, pk: Any
    ) -> read_schemas.ObservationOverviewSeriesConfigurationRead:
        db_item = await anyio.to_thread.run_sync(
            db.get_observation_overview_series_configuration, request.state.session, pk
        )
        return self._serialize_instance(db_item)

    async def find_all(
        self,
        request: Request,
        skip: int = 0,
        limit: int = 100,
        where: Union[dict[str, Any], str, None] = None,
        order_by: Optional[list[str]] = None,
    ) -> Sequence[read_schemas.ObservationSeriesConfigurationRead]:
        finder = functools.partial(
            db.collect_all_observation_overview_series_configurations,
        )
        db_items = await anyio.to_thread.run_sync(finder, request.state.session)
        return [self._serialize_instance(ind) for ind in db_items]

    async def count(
        self,
        request: Request,
        where: Union[dict[str, Any], str, None] = None,
    ) -> int:
        finder = functools.partial(
            db.collect_all_observation_overview_series_configurations,
        )
        found = await anyio.to_thread.run_sync(
            finder,
            request.state.session,
        )
        return len(found)


class ForecastOverviewSeriesConfigurationView(ModelView):
    identity = "forecast_overview_series_configurations"
    name = "Forecast Overview Series Configuration"
    label = "Forecasts"
    pk_attr = "id"

    exclude_fields_from_list = (
        "id",
        "netcdf_main_dataset_name",
        "thredds_url_pattern",
        "lower_uncertainty_thredds_url_pattern",
        "lower_uncertainty_netcdf_main_dataset_name",
        "upper_uncertainty_thredds_url_pattern",
        "upper_uncertainty_netcdf_main_dataset_name",
        "scenarios",
    )
    exclude_fields_from_detail = ("id",)
    exclude_fields_from_edit = ("identifier",)
    exclude_fields_from_create = ("identifier",)
    searchable_fields = ("climatic_indicator",)
    search_builder = False

    fields = (
        starlette_admin.IntegerField("id"),
        starlette_admin.StringField("identifier", read_only=True),
        starlette_admin.StringField(
            "netcdf_main_dataset_name",
            required=True,
            help_text=(
                "Name of the main variable inside this dataset's NetCDF file. This can "
                "be a templated value, such as '{historical_year_period}_avg'."
            ),
        ),
        starlette_admin.StringField(
            "thredds_url_pattern",
            required=True,
            help_text=_thredds_url_pattern_help_text,
        ),
        fields.RelatedClimaticIndicatorField(
            "climatic_indicator",
            help_text="climatic indicator",
            required=True,
        ),
        starlette_admin.StringField(
            "lower_uncertainty_thredds_url_pattern", required=False
        ),
        starlette_admin.StringField(
            "lower_uncertainty_netcdf_main_dataset_name",
            required=False,
            help_text=(
                "Name of the main variable inside this dataset's lower uncertainty "
                "NetCDF file. This can be a templated value, such "
                "as '{historical_year_period}_avg'."
            ),
        ),
        starlette_admin.StringField(
            "upper_uncertainty_thredds_url_pattern", required=False
        ),
        starlette_admin.StringField(
            "upper_uncertainty_netcdf_main_dataset_name",
            required=False,
            help_text=(
                "Name of the main variable inside this dataset's upper uncertainty "
                "NetCDF file. This can be a templated value, such "
                "as '{historical_year_period}_avg'."
            ),
        ),
        starlette_admin.EnumField(
            "scenarios", multiple=True, enum=static.ForecastScenario, required=True
        ),
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.icon = "fa-solid fa-map"

    @staticmethod
    def _serialize_instance(instance: overviews.ForecastOverviewSeriesConfiguration):
        return read_schemas.ForecastOverviewSeriesConfigurationRead(
            **instance.model_dump(
                exclude={
                    "scenarios",
                    "climatic_indicator",
                }
            ),
            scenarios=instance.scenarios or [],
            climatic_indicator=instance.climatic_indicator_id,
        )

    async def create(self, request: Request, data: dict[str, Any]) -> Any:
        try:
            data = await self._arrange_data(request, data)
            await self.validate(request, data)
            forecast_overview_series_configuration_create = (
                overviews.ForecastOverviewSeriesConfigurationCreate(
                    netcdf_main_dataset_name=data["netcdf_main_dataset_name"],
                    thredds_url_pattern=data["thredds_url_pattern"],
                    climatic_indicator_id=data["climatic_indicator"],
                    lower_uncertainty_thredds_url_pattern=data.get(
                        "lower_uncertainty_thredds_url_pattern"
                    ),
                    lower_uncertainty_netcdf_main_dataset_name=data.get(
                        "lower_uncertainty_netcdf_main_dataset_name"
                    ),
                    upper_uncertainty_thredds_url_pattern=data.get(
                        "upper_uncertainty_thredds_url_pattern"
                    ),
                    upper_uncertainty_netcdf_main_dataset_name=data.get(
                        "upper_uncertainty_netcdf_main_dataset_name"
                    ),
                    scenarios=data.get("scenarios", []),
                )
            )
            db_forecast_overview_series_configuration = await anyio.to_thread.run_sync(
                db.create_forecast_overview_series_configuration,
                request.state.session,
                forecast_overview_series_configuration_create,
            )
            return self._serialize_instance(db_forecast_overview_series_configuration)
        except Exception as e:
            return self.handle_exception(e)

    async def edit(self, request: Request, pk: Any, data: dict[str, Any]) -> Any:
        try:
            data = await self._arrange_data(request, data, True)
            await self.validate(request, data)
            forecast_overview_series_configuration_update = (
                overviews.ForecastOverviewSeriesConfigurationUpdate(
                    netcdf_main_dataset_name=data["netcdf_main_dataset_name"],
                    thredds_url_pattern=data["thredds_url_pattern"],
                    climatic_indicator_id=data["climatic_indicator"],
                    lower_uncertainty_thredds_url_pattern=data.get(
                        "lower_uncertainty_thredds_url_pattern"
                    ),
                    lower_uncertainty_netcdf_main_dataset_name=data.get(
                        "lower_uncertainty_netcdf_main_dataset_name"
                    ),
                    upper_uncertainty_thredds_url_pattern=data.get(
                        "upper_uncertainty_thredds_url_pattern"
                    ),
                    upper_uncertainty_netcdf_main_dataset_name=data.get(
                        "upper_uncertainty_netcdf_main_dataset_name"
                    ),
                    scenarios=data.get("scenarios", []),
                )
            )
            db_forecast_overview_series_configuration = await anyio.to_thread.run_sync(
                db.get_forecast_overview_series_configuration, request.state.session, pk
            )
            db_forecast_overview_series_configuration = await anyio.to_thread.run_sync(
                db.update_forecast_overview_series_configuration,
                request.state.session,
                db_forecast_overview_series_configuration,
                forecast_overview_series_configuration_update,
            )
            return self._serialize_instance(db_forecast_overview_series_configuration)
        except Exception as e:
            return self.handle_exception(e)

    async def find_by_pk(
        self, request: Request, pk: Any
    ) -> read_schemas.ForecastOverviewSeriesConfigurationRead:
        db_item = await anyio.to_thread.run_sync(
            db.get_forecast_overview_series_configuration, request.state.session, pk
        )
        return self._serialize_instance(db_item)

    async def find_all(
        self,
        request: Request,
        skip: int = 0,
        limit: int = 100,
        where: Union[dict[str, Any], str, None] = None,
        order_by: Optional[list[str]] = None,
    ) -> Sequence[read_schemas.ForecastOverviewSeriesConfigurationRead]:
        finder = functools.partial(
            db.collect_all_forecast_overview_series_configurations,
        )
        db_items = await anyio.to_thread.run_sync(finder, request.state.session)
        return [self._serialize_instance(ind) for ind in db_items]

    async def count(
        self,
        request: Request,
        where: Union[dict[str, Any], str, None] = None,
    ) -> int:
        finder = functools.partial(
            db.collect_all_forecast_overview_series_configurations,
        )
        found = await anyio.to_thread.run_sync(
            finder,
            request.state.session,
        )
        return len(found)
