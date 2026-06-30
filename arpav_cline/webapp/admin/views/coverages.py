"""Views for the admin app's coverages.

The classes contained in this module are derived from
starlette_admin.contrib.sqlmodel.ModelView. This is done mostly for two reasons:

1. To be able to control database access and ensure we are using our handlers
   defined in `arpav_cline.db` - this is meant for achieving consistency
   throughout the code, as the API is also using the mentioned functions for
   interacting with the DB

2. To be able to present inline forms for editing related objects, as is the
   case with parameter configuration and its related values.

"""

import functools
import logging
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
from ....schemas import (
    coverages,
    static,
)
from .. import (
    fields,
    schemas as read_schemas,
)

logger = logging.getLogger(__name__)


class ForecastTimeWindowView(ModelView):
    identity = "forecast_time_windows"
    name = "Forecast Time Window"
    label = "Time Windows"
    pk_attr = "id"

    exclude_fields_from_list = (
        "id",
        "internal_value",
        "display_name_english",
        "display_name_italian",
        "description_english",
        "description_italian",
    )
    exclude_fields_from_detail = ("id",)
    fields = (
        starlette_admin.IntegerField("id"),
        starlette_admin.StringField("name", required=True),
        starlette_admin.StringField("internal_value", required=True),
        starlette_admin.StringField("display_name_english", required=True),
        starlette_admin.StringField("display_name_italian", required=True),
        starlette_admin.StringField("description_english"),
        starlette_admin.StringField("description_italian"),
        starlette_admin.IntegerField("sort_order"),
    )
    search_builder = False

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.icon = "fa-solid fa-map"

    @staticmethod
    def _serialize_instance(
        instance: coverages.ForecastTimeWindow,
    ) -> read_schemas.ForecastTimeWindowRead:
        return read_schemas.ForecastTimeWindowRead(**instance.model_dump())

    async def create(self, request: Request, data: dict[str, Any]) -> Any:
        try:
            data = await self._arrange_data(request, data)
            await self.validate(request, data)
            forecast_time_window_create = coverages.ForecastTimeWindowCreate(**data)
            db_forecast_time_window = await anyio.to_thread.run_sync(
                db.create_forecast_time_window,
                request.state.session,
                forecast_time_window_create,
            )
            return self._serialize_instance(db_forecast_time_window)
        except Exception as e:
            return self.handle_exception(e)

    async def edit(self, request: Request, pk: Any, data: dict[str, Any]) -> Any:
        try:
            data = await self._arrange_data(request, data, True)
            await self.validate(request, data)
            forecast_time_window_update = coverages.ForecastTimeWindowUpdate(**data)
            db_forecast_time_window = await anyio.to_thread.run_sync(
                db.get_forecast_time_window,
                request.state.session,
                pk,
            )
            db_forecast_time_window = await anyio.to_thread.run_sync(
                db.update_forecast_time_window,
                request.state.session,
                db_forecast_time_window,
                forecast_time_window_update,
            )
            return self._serialize_instance(db_forecast_time_window)
        except Exception as e:
            self.handle_exception(e)

    async def find_by_pk(
        self, request: Request, pk: Any
    ) -> read_schemas.ForecastTimeWindowRead:
        db_forecast_time_window = await anyio.to_thread.run_sync(
            db.get_forecast_time_window, request.state.session, pk
        )
        return self._serialize_instance(db_forecast_time_window)

    async def find_all(
        self,
        request: Request,
        skip: int = 0,
        limit: int = 100,
        where: Union[dict[str, Any], str, None] = None,
        order_by: Optional[list[str]] = None,
    ) -> Sequence[read_schemas.ForecastTimeWindowRead]:
        list_params = functools.partial(
            db.list_forecast_time_windows,
            limit=limit,
            offset=skip,
            name_filter=str(where) if where not in (None, "") else None,
            include_total=False,
        )
        db_forecast_time_windows, _ = await anyio.to_thread.run_sync(
            list_params, request.state.session
        )
        return [self._serialize_instance(fm) for fm in db_forecast_time_windows]


class ForecastModelView(ModelView):
    identity = "forecast_models"
    name = "Forecast Model"
    label = "Models"
    pk_attr = "id"

    exclude_fields_from_list = (
        "id",
        "internal_value",
        "display_name_english",
        "display_name_italian",
        "description_english",
        "description_italian",
    )
    exclude_fields_from_detail = ("id",)
    fields = (
        starlette_admin.IntegerField("id"),
        starlette_admin.StringField("name", required=True),
        starlette_admin.StringField("internal_value", required=True),
        starlette_admin.StringField("display_name_english", required=True),
        starlette_admin.StringField("display_name_italian", required=True),
        starlette_admin.StringField("description_english"),
        starlette_admin.StringField("description_italian"),
        starlette_admin.IntegerField("sort_order"),
    )
    search_builder = False

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.icon = "fa-solid fa-map"

    @staticmethod
    def _serialize_instance(
        instance: coverages.ForecastModel,
    ) -> read_schemas.ForecastModelRead:
        return read_schemas.ForecastModelRead(**instance.model_dump())

    async def create(self, request: Request, data: dict[str, Any]) -> Any:
        try:
            data = await self._arrange_data(request, data)
            await self.validate(request, data)
            forecast_model_create = coverages.ForecastModelCreate(**data)
            db_forecast_model = await anyio.to_thread.run_sync(
                db.create_forecast_model,
                request.state.session,
                forecast_model_create,
            )
            return self._serialize_instance(db_forecast_model)
        except Exception as e:
            return self.handle_exception(e)

    async def edit(self, request: Request, pk: Any, data: dict[str, Any]) -> Any:
        try:
            data = await self._arrange_data(request, data, True)
            await self.validate(request, data)
            forecast_model_update = coverages.ForecastModelUpdate(**data)
            db_forecast_model = await anyio.to_thread.run_sync(
                db.get_forecast_model,
                request.state.session,
                pk,
            )
            db_forecast_model = await anyio.to_thread.run_sync(
                db.update_forecast_model,
                request.state.session,
                db_forecast_model,
                forecast_model_update,
            )
            return self._serialize_instance(db_forecast_model)
        except Exception as e:
            self.handle_exception(e)

    async def find_by_pk(
        self, request: Request, pk: Any
    ) -> read_schemas.ForecastModelRead:
        db_forecast_model = await anyio.to_thread.run_sync(
            db.get_forecast_model, request.state.session, pk
        )
        return self._serialize_instance(db_forecast_model)

    async def find_all(
        self,
        request: Request,
        skip: int = 0,
        limit: int = 100,
        where: Union[dict[str, Any], str, None] = None,
        order_by: Optional[list[str]] = None,
    ) -> Sequence[read_schemas.ForecastModelRead]:
        list_params = functools.partial(
            db.list_forecast_models,
            limit=limit,
            offset=skip,
            name_filter=str(where) if where not in (None, "") else None,
            include_total=False,
        )
        db_forecast_models, _ = await anyio.to_thread.run_sync(
            list_params, request.state.session
        )
        return [self._serialize_instance(fm) for fm in db_forecast_models]


class ForecastModelGroupView(ModelView):
    identity = "forecast_model_groups"
    name = "Forecast Model Group"
    label = "Model Groups"
    pk_attr = "id"

    exclude_fields_from_list = (
        "id",
        "display_name_english",
        "display_name_italian",
        "description_english",
        "description_italian",
    )
    exclude_fields_from_detail = ("id",)
    fields = (
        starlette_admin.IntegerField("id"),
        starlette_admin.StringField("name", required=True),
        starlette_admin.StringField("display_name_english", required=True),
        starlette_admin.StringField("display_name_italian", required=True),
        starlette_admin.StringField("description_english"),
        starlette_admin.StringField("description_italian"),
        starlette_admin.IntegerField("sort_order"),
        fields.RelatedForecastModelsField(
            "forecast_models", multiple=True, required=True
        ),
    )
    search_builder = False

    @staticmethod
    def _serialize_instance(
        instance: coverages.ForecastModelGroup,
    ) -> read_schemas.ForecastModelGroupRead:
        return read_schemas.ForecastModelGroupRead(
            **instance.model_dump(),
            forecast_models=[
                fml.forecast_model_id for fml in instance.forecast_model_links
            ],
        )

    async def create(self, request: Request, data: dict[str, Any]) -> Any:
        try:
            data = await self._arrange_data(request, data)
            await self.validate(request, data)
            forecast_model_group_create = coverages.ForecastModelGroupCreate(**data)
            db_forecast_model_group = await anyio.to_thread.run_sync(
                db.create_forecast_model_group,
                request.state.session,
                forecast_model_group_create,
            )
            return self._serialize_instance(db_forecast_model_group)
        except Exception as e:
            return self.handle_exception(e)

    async def edit(self, request: Request, pk: Any, data: dict[str, Any]) -> Any:
        try:
            data = await self._arrange_data(request, data, True)
            await self.validate(request, data)
            forecast_model_group_update = coverages.ForecastModelGroupUpdate(**data)
            db_forecast_model_group = await anyio.to_thread.run_sync(
                db.get_forecast_model_group,
                request.state.session,
                pk,
            )
            db_forecast_model_group = await anyio.to_thread.run_sync(
                db.update_forecast_model_group,
                request.state.session,
                db_forecast_model_group,
                forecast_model_group_update,
            )
            return self._serialize_instance(db_forecast_model_group)
        except Exception as e:
            self.handle_exception(e)

    async def find_by_pk(
        self, request: Request, pk: Any
    ) -> read_schemas.ForecastModelGroupRead:
        db_forecast_model_group = await anyio.to_thread.run_sync(
            db.get_forecast_model_group, request.state.session, pk
        )
        return self._serialize_instance(db_forecast_model_group)

    async def find_all(
        self,
        request: Request,
        skip: int = 0,
        limit: int = 100,
        where: Union[dict[str, Any], str, None] = None,
        order_by: Optional[list[str]] = None,
    ) -> Sequence[read_schemas.ForecastModelGroupRead]:
        list_params = functools.partial(
            db.list_forecast_model_groups,
            limit=limit,
            offset=skip,
            name_filter=str(where) if where not in (None, "") else None,
            include_total=False,
        )
        db_forecast_model_groups, _ = await anyio.to_thread.run_sync(
            list_params, request.state.session
        )
        return [self._serialize_instance(fm) for fm in db_forecast_model_groups]


class ForecastYearPeriodGroupView(ModelView):
    identity = "forecast_year_period_groups"
    name = "Forecast Year Period Group"
    label = "Year Period Groups"
    pk_attr = "id"

    exclude_fields_from_list = (
        "id",
        "display_name_english",
        "display_name_italian",
        "description_english",
        "description_italian",
    )
    exclude_fields_from_detail = ("id",)
    fields = (
        starlette_admin.IntegerField("id"),
        starlette_admin.StringField("name", required=True),
        starlette_admin.StringField("display_name_english", required=True),
        starlette_admin.StringField("display_name_italian", required=True),
        starlette_admin.StringField("description_english"),
        starlette_admin.StringField("description_italian"),
        starlette_admin.IntegerField("sort_order"),
        starlette_admin.EnumField(
            "year_periods", multiple=True, enum=static.ForecastYearPeriod, required=True
        ),
    )
    search_builder = False

    @staticmethod
    def _serialize_instance(
        instance: coverages.ForecastYearPeriodGroup,
    ) -> read_schemas.ForecastYearPeriodGroupRead:
        return read_schemas.ForecastYearPeriodGroupRead(**instance.model_dump())

    async def create(self, request: Request, data: dict[str, Any]) -> Any:
        try:
            data = await self._arrange_data(request, data)
            await self.validate(request, data)
            forecast_year_period_group_create = coverages.ForecastYearPeriodGroupCreate(
                **data
            )
            db_forecast_year_period_group = await anyio.to_thread.run_sync(
                db.create_forecast_year_period_group,
                request.state.session,
                forecast_year_period_group_create,
            )
            return self._serialize_instance(db_forecast_year_period_group)
        except Exception as e:
            return self.handle_exception(e)

    async def edit(self, request: Request, pk: Any, data: dict[str, Any]) -> Any:
        try:
            data = await self._arrange_data(request, data, True)
            await self.validate(request, data)
            forecast_year_period_group_update = coverages.ForecastYearPeriodGroupUpdate(
                **data
            )
            db_forecast_year_period_group = await anyio.to_thread.run_sync(
                db.get_forecast_year_period_group,
                request.state.session,
                pk,
            )
            db_forecast_year_period_group = await anyio.to_thread.run_sync(
                db.update_forecast_year_period_group,
                request.state.session,
                db_forecast_year_period_group,
                forecast_year_period_group_update,
            )
            return self._serialize_instance(db_forecast_year_period_group)
        except Exception as e:
            self.handle_exception(e)

    async def find_by_pk(
        self, request: Request, pk: Any
    ) -> read_schemas.ForecastYearPeriodGroupRead:
        db_forecast_year_period_group = await anyio.to_thread.run_sync(
            db.get_forecast_year_period_group, request.state.session, pk
        )
        return self._serialize_instance(db_forecast_year_period_group)

    async def find_all(
        self,
        request: Request,
        skip: int = 0,
        limit: int = 100,
        where: Union[dict[str, Any], str, None] = None,
        order_by: Optional[list[str]] = None,
    ) -> Sequence[read_schemas.ForecastYearPeriodGroupRead]:
        list_params = functools.partial(
            db.list_forecast_year_period_groups,
            limit=limit,
            offset=skip,
            name_filter=str(where) if where not in (None, "") else None,
            include_total=False,
        )
        db_forecast_year_period_groups, _ = await anyio.to_thread.run_sync(
            list_params, request.state.session
        )
        return [self._serialize_instance(fm) for fm in db_forecast_year_period_groups]


class HistoricalYearPeriodGroupView(ModelView):
    identity = "historical_year_period_groups"
    name = "Historical Year Period Group"
    label = "Year Period Groups"
    pk_attr = "id"

    exclude_fields_from_list = (
        "id",
        "display_name_english",
        "display_name_italian",
        "description_english",
        "description_italian",
    )
    exclude_fields_from_detail = ("id",)
    fields = (
        starlette_admin.IntegerField("id"),
        starlette_admin.StringField("name", required=True),
        starlette_admin.StringField("display_name_english", required=True),
        starlette_admin.StringField("display_name_italian", required=True),
        starlette_admin.StringField("description_english"),
        starlette_admin.StringField("description_italian"),
        starlette_admin.IntegerField("sort_order"),
        starlette_admin.EnumField(
            "year_periods",
            multiple=True,
            enum=static.HistoricalYearPeriod,
            required=True,
        ),
    )
    search_builder = False

    @staticmethod
    def _serialize_instance(
        instance: coverages.HistoricalYearPeriodGroup,
    ) -> read_schemas.HistoricalYearPeriodGroupRead:
        return read_schemas.HistoricalYearPeriodGroupRead(**instance.model_dump())

    async def create(self, request: Request, data: dict[str, Any]) -> Any:
        try:
            data = await self._arrange_data(request, data)
            await self.validate(request, data)
            historical_year_period_group_create = (
                coverages.HistoricalYearPeriodGroupCreate(**data)
            )
            db_historical_year_period_group = await anyio.to_thread.run_sync(
                db.create_historical_year_period_group,
                request.state.session,
                historical_year_period_group_create,
            )
            return self._serialize_instance(db_historical_year_period_group)
        except Exception as e:
            return self.handle_exception(e)

    async def edit(self, request: Request, pk: Any, data: dict[str, Any]) -> Any:
        try:
            data = await self._arrange_data(request, data, True)
            await self.validate(request, data)
            historical_year_period_group_update = (
                coverages.HistoricalYearPeriodGroupUpdate(**data)
            )
            db_historical_year_period_group = await anyio.to_thread.run_sync(
                db.get_historical_year_period_group,
                request.state.session,
                pk,
            )
            db_historical_year_period_group = await anyio.to_thread.run_sync(
                db.update_historical_year_period_group,
                request.state.session,
                db_historical_year_period_group,
                historical_year_period_group_update,
            )
            return self._serialize_instance(db_historical_year_period_group)
        except Exception as e:
            self.handle_exception(e)

    async def find_by_pk(
        self, request: Request, pk: Any
    ) -> read_schemas.HistoricalYearPeriodGroupRead:
        db_historical_year_period_group = await anyio.to_thread.run_sync(
            db.get_historical_year_period_group, request.state.session, pk
        )
        return self._serialize_instance(db_historical_year_period_group)

    async def find_all(
        self,
        request: Request,
        skip: int = 0,
        limit: int = 100,
        where: Union[dict[str, Any], str, None] = None,
        order_by: Optional[list[str]] = None,
    ) -> Sequence[read_schemas.HistoricalYearPeriodGroupRead]:
        list_params = functools.partial(
            db.list_historical_year_period_groups,
            limit=limit,
            offset=skip,
            name_filter=str(where) if where not in (None, "") else None,
            include_total=False,
        )
        db_historical_year_period_groups, _ = await anyio.to_thread.run_sync(
            list_params, request.state.session
        )
        return [self._serialize_instance(fm) for fm in db_historical_year_period_groups]


class ForecastCoverageConfigurationView(ModelView):
    identity = "forecast_coverage_configurations"
    name = "Forecast Coverage Configuration"
    label = "Coverage Configurations"
    pk_attr = "id"

    exclude_fields_from_list = (
        "id",
        "include_in_advanced_section_combinations",
        "include_in_simple_section_combinations",
        "identifier",
        "netcdf_main_dataset_name",
        "thredds_url_pattern",
        "wms_main_layer_name",
        "wms_secondary_layer_name",
        "lower_uncertainty_thredds_url_pattern",
        "lower_uncertainty_netcdf_main_dataset_name",
        "observation_series_configurations",
        "scenarios",
        "spatial_region",
        "time_windows",
        "upper_uncertainty_thredds_url_pattern",
        "upper_uncertainty_netcdf_main_dataset_name",
    )
    exclude_fields_from_detail = ("id",)
    exclude_fields_from_edit = ("identifier",)
    exclude_fields_from_create = ("identifier",)
    searchable_fields = ("climatic_indicator",)
    search_builder = False

    fields = (
        starlette_admin.IntegerField("id"),
        starlette_admin.StringField("identifier", read_only=True),
        starlette_admin.BooleanField(
            "include_in_advanced_section_combinations", required=True
        ),
        starlette_admin.BooleanField(
            "include_in_simple_section_combinations", required=True
        ),
        fields.RelatedClimaticIndicatorField(
            "climatic_indicator",
            help_text="climatic indicator",
            required=True,
        ),
        fields.RelatedSpatialRegionField(
            "spatial_region",
            required=True,
        ),
        starlette_admin.EnumField(
            "scenarios", multiple=True, enum=static.ForecastScenario, required=True
        ),
        fields.RelatedForecastYearPeriodGroupField("year_period_group", required=True),
        fields.RelatedForecastModelGroupField("forecast_model_group", required=True),
        fields.RelatedForecastTimeWindowField(
            "time_windows",
            multiple=True,
        ),
        fields.RelatedObservationSeriesConfigurationField(
            "observation_series_configurations",
            multiple=True,
        ),
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
            help_text=(
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
            ),
        ),
        starlette_admin.StringField("wms_main_layer_name", required=True),
        starlette_admin.StringField("wms_secondary_layer_name", required=False),
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
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.icon = "fa-solid fa-map"

    @staticmethod
    def _serialize_instance(instance: coverages.ForecastCoverageConfiguration):
        return read_schemas.ForecastCoverageConfigurationRead(
            **instance.model_dump(
                exclude={
                    "climatic_indicator",
                    "spatial_region",
                    "forecast_model_group",
                    "year_period_group",
                }
            ),
            climatic_indicator=instance.climatic_indicator_id,
            forecast_model_group=instance.forecast_model_group_id,
            year_period_group=instance.year_period_group_id,
            spatial_region=instance.spatial_region_id,
            time_windows=[
                twl.forecast_time_window_id
                for twl in instance.forecast_time_window_links
            ],
            observation_series_configurations=[
                oscl.observation_series_configuration_id
                for oscl in instance.observation_series_configuration_links
            ],
        )

    async def create(self, request: Request, data: dict[str, Any]) -> Any:
        try:
            data = await self._arrange_data(request, data)
            await self.validate(request, data)
            forecast_coverage_configuration_create = (
                coverages.ForecastCoverageConfigurationCreate(
                    netcdf_main_dataset_name=data["netcdf_main_dataset_name"],
                    thredds_url_pattern=data["thredds_url_pattern"],
                    wms_main_layer_name=data["wms_main_layer_name"],
                    wms_secondary_layer_name=data.get(
                        "wms_secondary_layer_name", data["wms_main_layer_name"]
                    ),
                    climatic_indicator_id=data["climatic_indicator"],
                    spatial_region_id=data["spatial_region"],
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
                    year_period_group=data["year_period_group"],
                    forecast_model_group=data["forecast_model_group"],
                    time_windows=data["time_windows"],
                    observation_series_configurations=data[
                        "observation_series_configurations"
                    ],
                    include_in_advanced_section_combinations=data[
                        "include_in_advanced_section_combinations"
                    ],
                    include_in_simple_section_combinations=data[
                        "include_in_simple_section_combinations"
                    ],
                )
            )
            db_forecast_coverage_configuration = await anyio.to_thread.run_sync(
                db.create_forecast_coverage_configuration,
                request.state.session,
                forecast_coverage_configuration_create,
            )
            return self._serialize_instance(db_forecast_coverage_configuration)
        except Exception as e:
            return self.handle_exception(e)

    async def edit(self, request: Request, pk: Any, data: dict[str, Any]) -> Any:
        try:
            data = await self._arrange_data(request, data, True)
            logger.debug(f"before validation {data=}")
            await self.validate(request, data)
            logger.debug(f"after validation {data=}")
            forecast_coverage_configuration_create = (
                coverages.ForecastCoverageConfigurationUpdate(
                    netcdf_main_dataset_name=data["netcdf_main_dataset_name"],
                    thredds_url_pattern=data["thredds_url_pattern"],
                    wms_main_layer_name=data["wms_main_layer_name"],
                    wms_secondary_layer_name=data.get(
                        "wms_secondary_layer_name", data["wms_main_layer_name"]
                    ),
                    climatic_indicator_id=data["climatic_indicator"],
                    spatial_region_id=data["spatial_region"],
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
                    year_period_group=data.get("year_period_group"),
                    forecast_model_group=data.get("forecast_model_group"),
                    time_windows=data.get("time_windows"),
                    observation_series_configurations=data.get(
                        "observation_series_configurations"
                    ),
                    include_in_advanced_section_combinations=data[
                        "include_in_advanced_section_combinations"
                    ],
                    include_in_simple_section_combinations=data[
                        "include_in_simple_section_combinations"
                    ],
                )
            )
            db_forecast_coverage_configuration = await anyio.to_thread.run_sync(
                db.get_forecast_coverage_configuration, request.state.session, pk
            )
            db_forecast_coverage_configuration = await anyio.to_thread.run_sync(
                db.update_forecast_coverage_configuration,
                request.state.session,
                db_forecast_coverage_configuration,
                forecast_coverage_configuration_create,
            )
            return self._serialize_instance(db_forecast_coverage_configuration)
        except Exception as e:
            return self.handle_exception(e)

    async def find_by_pk(
        self, request: Request, pk: Any
    ) -> read_schemas.ForecastCoverageConfigurationRead:
        db_item = await anyio.to_thread.run_sync(
            db.get_forecast_coverage_configuration, request.state.session, pk
        )
        return self._serialize_instance(db_item)

    async def find_all(
        self,
        request: Request,
        skip: int = 0,
        limit: int = 100,
        where: Union[dict[str, Any], str, None] = None,
        order_by: Optional[list[str]] = None,
    ) -> Sequence[read_schemas.ForecastCoverageConfigurationRead]:
        finder = functools.partial(
            db.collect_all_forecast_coverage_configurations_with_identifier_filter,
            identifier_filter=str(where) if where else None,
        )
        db_items = await anyio.to_thread.run_sync(finder, request.state.session)
        return [self._serialize_instance(ind) for ind in db_items]

    async def count(
        self,
        request: Request,
        where: Union[dict[str, Any], str, None] = None,
    ) -> int:
        finder = functools.partial(
            db.collect_all_forecast_coverage_configurations_with_identifier_filter,
            identifier_filter=str(where) if where else None,
        )
        found = await anyio.to_thread.run_sync(
            finder,
            request.state.session,
        )
        return len(found)


class HistoricalCoverageConfigurationView(ModelView):
    identity = "historical_coverage_configurations"
    name = "Historical Coverage Configuration"
    label = "Coverage Configurations"
    pk_attr = "id"

    exclude_fields_from_list = (
        "decades",
        "id",
        "include_in_advanced_section_combinations",
        "include_in_simple_section_combinations",
        "identifier",
        "netcdf_main_dataset_name",
        "observation_series_configurations",
        "reference_period",
        "spatial_region",
        "thredds_url_pattern",
        "wms_main_layer_name",
    )
    exclude_fields_from_detail = ("id",)
    exclude_fields_from_edit = ("identifier",)
    exclude_fields_from_create = ("identifier",)
    searchable_fields = ("climatic_indicator",)
    search_builder = False

    fields = (
        starlette_admin.IntegerField("id"),
        starlette_admin.StringField("identifier", read_only=True),
        starlette_admin.BooleanField(
            "include_in_advanced_section_combinations", required=True
        ),
        starlette_admin.BooleanField(
            "include_in_simple_section_combinations", required=True
        ),
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
            help_text=(
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
            ),
        ),
        starlette_admin.StringField("wms_main_layer_name", required=True),
        fields.RelatedClimaticIndicatorField(
            "climatic_indicator",
            help_text="climatic indicator",
            required=True,
        ),
        fields.RelatedSpatialRegionField(
            "spatial_region",
            required=True,
        ),
        starlette_admin.EnumField(
            "reference_period", enum=static.HistoricalReferencePeriod, required=False
        ),
        starlette_admin.EnumField(
            "decades", multiple=True, enum=static.HistoricalDecade, required=False
        ),
        fields.RelatedHistoricalYearPeriodGroupField("year_period_group"),
        fields.RelatedObservationSeriesConfigurationField(
            "observation_series_configurations",
            multiple=True,
            required=True,
        ),
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.icon = "fa-solid fa-map"

    @staticmethod
    def _serialize_instance(
        instance: coverages.HistoricalCoverageConfiguration,
    ):
        return read_schemas.HistoricalCoverageConfigurationRead(
            **instance.model_dump(
                exclude={
                    "climatic_indicator",
                    "spatial_region",
                    "decades",
                    "observation_series_configurations",
                    "year_period_group",
                }
            ),
            climatic_indicator=instance.climatic_indicator_id,
            spatial_region=instance.spatial_region_id,
            decades=instance.decades or [],
            year_period_group=instance.year_period_group_id,
            observation_series_configurations=[
                oscl.observation_series_configuration_id
                for oscl in instance.observation_series_configuration_links
            ],
        )

    async def create(self, request: Request, data: dict[str, Any]) -> Any:
        try:
            data = await self._arrange_data(request, data)
            await self.validate(request, data)
            historical_coverage_configuration_create = (
                coverages.HistoricalCoverageConfigurationCreate(
                    netcdf_main_dataset_name=data["netcdf_main_dataset_name"],
                    thredds_url_pattern=data["thredds_url_pattern"],
                    wms_main_layer_name=data["wms_main_layer_name"],
                    climatic_indicator_id=data["climatic_indicator"],
                    spatial_region_id=data["spatial_region"],
                    reference_period=data.get("reference_period"),
                    decades=data.get("decades", []),
                    year_period_group=data["year_period_group"],
                    observation_series_configurations=data[
                        "observation_series_configurations"
                    ],
                    include_in_advanced_section_combinations=data[
                        "include_in_advanced_section_combinations"
                    ],
                    include_in_simple_section_combinations=data[
                        "include_in_simple_section_combinations"
                    ],
                )
            )
            db_historical_coverage_configuration = await anyio.to_thread.run_sync(
                db.create_historical_coverage_configuration,
                request.state.session,
                historical_coverage_configuration_create,
            )
            return self._serialize_instance(db_historical_coverage_configuration)
        except Exception as e:
            return self.handle_exception(e)

    async def edit(self, request: Request, pk: Any, data: dict[str, Any]) -> Any:
        try:
            data = await self._arrange_data(request, data, True)
            await self.validate(request, data)
            historical_coverage_configuration_create = (
                coverages.HistoricalCoverageConfigurationUpdate(
                    netcdf_main_dataset_name=data["netcdf_main_dataset_name"],
                    thredds_url_pattern=data["thredds_url_pattern"],
                    wms_main_layer_name=data["wms_main_layer_name"],
                    climatic_indicator_id=data["climatic_indicator"],
                    spatial_region_id=data["spatial_region"],
                    reference_period=data.get("reference_period"),
                    decades=data.get("decades", []),
                    year_period_group=data.get("year_period_group"),
                    observation_series_configurations=data[
                        "observation_series_configurations"
                    ],
                    include_in_advanced_section_combinations=data[
                        "include_in_advanced_section_combinations"
                    ],
                    include_in_simple_section_combinations=data[
                        "include_in_simple_section_combinations"
                    ],
                )
            )
            db_historical_coverage_configuration = await anyio.to_thread.run_sync(
                db.get_historical_coverage_configuration, request.state.session, pk
            )
            db_historical_coverage_configuration = await anyio.to_thread.run_sync(
                db.update_historical_coverage_configuration,
                request.state.session,
                db_historical_coverage_configuration,
                historical_coverage_configuration_create,
            )
            return self._serialize_instance(db_historical_coverage_configuration)
        except Exception as e:
            return self.handle_exception(e)

    async def find_by_pk(
        self, request: Request, pk: Any
    ) -> read_schemas.HistoricalCoverageConfigurationRead:
        db_item = await anyio.to_thread.run_sync(
            db.get_historical_coverage_configuration, request.state.session, pk
        )
        return self._serialize_instance(db_item)

    async def find_all(
        self,
        request: Request,
        skip: int = 0,
        limit: int = 100,
        where: Union[dict[str, Any], str, None] = None,
        order_by: Optional[list[str]] = None,
    ) -> Sequence[read_schemas.HistoricalCoverageConfigurationRead]:
        finder = functools.partial(
            db.collect_all_historical_coverage_configurations_with_identifier_filter,
            identifier_filter=str(where) if where else None,
        )
        db_items = await anyio.to_thread.run_sync(finder, request.state.session)
        return [self._serialize_instance(ind) for ind in db_items]

    async def count(
        self,
        request: Request,
        where: Union[dict[str, Any], str, None] = None,
    ) -> int:
        finder = functools.partial(
            db.collect_all_historical_coverage_configurations_with_identifier_filter,
            identifier_filter=str(where) if where else None,
        )
        found = await anyio.to_thread.run_sync(
            finder,
            request.state.session,
        )
        return len(found)
