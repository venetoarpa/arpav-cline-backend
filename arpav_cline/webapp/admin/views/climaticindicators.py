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
from ....schemas.static import (
    AggregationPeriod,
    MeasureType,
    ObservationStationManager,
)
from ....schemas import climaticindicators
from .. import (
    fields,
    schemas as read_schemas,
)

logger = logging.getLogger(__name__)


class ClimaticIndicatorView(ModelView):
    identity = "climatic_indicators"
    name = "Climatic Indicator"
    label = "Climatic Indicators"
    pk_attr = "id"

    exclude_fields_from_list = (
        "id",
        "name",
        "historical_coverages_internal_name",
        "measure_type",
        "aggregation_period",
        "display_name_english",
        "display_name_italian",
        "description_english",
        "description_italian",
        "unit_english",
        "unit_italian",
        "palette",
        "color_scale_min",
        "color_scale_max",
        "data_precision",
        "observation_names",
        "forecast_model_base_paths",
    )
    exclude_fields_from_detail = ("id",)
    exclude_fields_from_edit = ("identifier",)
    exclude_fields_from_create = ("identifier",)
    search_builder = False

    fields = (
        starlette_admin.IntegerField("id"),
        starlette_admin.StringField("identifier", read_only=True),
        starlette_admin.StringField("name", required=True),
        starlette_admin.StringField("historical_coverages_internal_name"),
        starlette_admin.EnumField("measure_type", enum=MeasureType, required=True),
        starlette_admin.EnumField(
            "aggregation_period", enum=AggregationPeriod, required=True
        ),
        starlette_admin.StringField("display_name_english", required=True),
        starlette_admin.StringField("display_name_italian", required=True),
        starlette_admin.StringField("description_english", required=True),
        starlette_admin.StringField("description_italian", required=True),
        starlette_admin.StringField("unit_english", required=True),
        starlette_admin.StringField("unit_italian", required=True),
        starlette_admin.StringField(
            "palette",
            required=True,
            help_text=(
                "Name of the palette that should used by the THREDDS WMS server. "
                "Available values can be found at https://reading-escience-centre.gitbooks.io/ncwms-user-guide/content/04-usage.html#getmap"
            ),
        ),
        starlette_admin.FloatField("color_scale_min", required=True),
        starlette_admin.FloatField("color_scale_max", required=True),
        starlette_admin.StringField("sort_order"),
        starlette_admin.IntegerField(
            "data_precision",
            required=True,
            help_text=(
                "Number of decimal places to be used when displaying data values"
            ),
        ),
        starlette_admin.ListField(
            starlette_admin.CollectionField(
                name="observation_names",
                fields=[
                    starlette_admin.EnumField(
                        "station_manager", enum=ObservationStationManager, required=True
                    ),
                    starlette_admin.StringField(
                        "indicator_observation_name", required=True
                    ),
                ],
            ),
        ),
        starlette_admin.ListField(
            starlette_admin.CollectionField(
                name="forecast_model_base_paths",
                fields=[
                    fields.RelatedForecastModelField(
                        "forecast_model",
                        required=True,
                    ),
                    starlette_admin.StringField("thredds_url_base_path", required=True),
                    starlette_admin.StringField("thredds_url_uncertainties_base_path"),
                ],
            ),
        ),
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.icon = "fa-solid fa-cloud-sun-rain"

    @staticmethod
    def _serialize_instance(instance: climaticindicators.ClimaticIndicator):
        return read_schemas.ClimaticIndicatorRead(
            **instance.model_dump(),
            observation_names=[
                read_schemas.ClimaticIndicatorObservationNameRead(
                    station_manager=obs_name.station_manager,
                    indicator_observation_name=obs_name.indicator_observation_name,
                )
                for obs_name in instance.observation_names
            ],
            forecast_model_base_paths=[
                read_schemas.ClimaticIndicatorForecastModelBasePathRead(
                    forecast_model=fm.forecast_model_id,
                    thredds_url_base_path=fm.thredds_url_base_path,
                    thredds_url_uncertainties_base_path=fm.thredds_url_uncertainties_base_path,
                )
                for fm in instance.forecast_model_links
            ],
        )

    async def create(self, request: Request, data: dict[str, Any]) -> Any:
        try:
            data = await self._arrange_data(request, data)
            await self.validate(request, data)
            climatic_indicator_create = climaticindicators.ClimaticIndicatorCreate(
                name=data["name"],
                historical_coverages_internal_name=data.get(
                    "historical_coverages_internal_name"
                ),
                measure_type=data["measure_type"],
                aggregation_period=data["aggregation_period"],
                display_name_english=data["display_name_english"],
                display_name_italian=data["display_name_italian"],
                description_english=data["description_english"],
                description_italian=data["description_italian"],
                unit_english=data["unit_english"],
                unit_italian=data["unit_italian"],
                palette=data["palette"],
                color_scale_min=data["color_scale_min"],
                color_scale_max=data["color_scale_max"],
                data_precision=data["data_precision"],
                sort_order=data.get("sort_order"),
                forecast_models=[
                    climaticindicators.ClimaticIndicatorForecastModelLinkCreateEmbeddedInClimaticIndicator(
                        forecast_model_id=fm["forecast_model"],
                        thredds_url_base_path=fm["thredds_url_base_path"],
                        thredds_url_uncertainties_base_path=fm.get(
                            "thredds_url_uncertainties_base_path"
                        ),
                    )
                    for fm in data.get("forecast_model_base_paths", [])
                ],
                observation_names=[
                    climaticindicators.ClimaticIndicatorObservationNameCreate(
                        observation_station_manager=obs_name["station_manager"],
                        indicator_observation_name=obs_name[
                            "indicator_observation_name"
                        ],
                    )
                    for obs_name in data.get("observation_names", [])
                ],
            )
            db_climatic_indicator = await anyio.to_thread.run_sync(
                db.create_climatic_indicator,
                request.state.session,
                climatic_indicator_create,
            )
            return self._serialize_instance(db_climatic_indicator)
        except Exception as e:
            return self.handle_exception(e)

    async def edit(self, request: Request, pk: Any, data: dict[str, Any]) -> Any:
        try:
            data = await self._arrange_data(request, data, True)
            await self.validate(request, data)
            climatic_indicator_update = climaticindicators.ClimaticIndicatorUpdate(
                name=data["name"],
                historical_coverages_internal_name=data.get(
                    "historical_coverages_internal_name"
                ),
                measure_type=data["measure_type"],
                aggregation_period=data["aggregation_period"],
                display_name_english=data["display_name_english"],
                display_name_italian=data["display_name_italian"],
                description_english=data["description_english"],
                description_italian=data["description_italian"],
                unit_english=data["unit_english"],
                unit_italian=data["unit_italian"],
                palette=data["palette"],
                color_scale_min=data["color_scale_min"],
                color_scale_max=data["color_scale_max"],
                data_precision=data["data_precision"],
                sort_order=data.get("sort_order"),
                observation_names=[
                    climaticindicators.ClimaticIndicatorObservationNameUpdate(
                        observation_station_manager=obs_name["station_manager"],
                        indicator_observation_name=obs_name[
                            "indicator_observation_name"
                        ],
                    )
                    for obs_name in data.get("observation_names", [])
                ],
                forecast_models=[
                    climaticindicators.ClimaticIndicatorForecastModelLinkUpdateEmbeddedInClimaticIndicator(
                        forecast_model_id=fm["forecast_model"],
                        thredds_url_base_path=fm["thredds_url_base_path"],
                        thredds_url_uncertainties_base_path=fm.get(
                            "thredds_url_uncertainties_base_path"
                        ),
                    )
                    for fm in data.get("forecast_model_base_paths", [])
                ],
            )
            db_climatic_indicator = await anyio.to_thread.run_sync(
                db.get_climatic_indicator, request.state.session, pk
            )
            db_climatic_indicator = await anyio.to_thread.run_sync(
                db.update_climatic_indicator,
                request.state.session,
                db_climatic_indicator,
                climatic_indicator_update,
            )
            return self._serialize_instance(db_climatic_indicator)
        except Exception as e:
            self.handle_exception(e)

    async def find_by_pk(
        self, request: Request, pk: Any
    ) -> read_schemas.ClimaticIndicatorRead:
        db_climatic_indicator = await anyio.to_thread.run_sync(
            db.get_climatic_indicator, request.state.session, pk
        )
        return self._serialize_instance(db_climatic_indicator)

    async def find_all(
        self,
        request: Request,
        skip: int = 0,
        limit: int = 100,
        where: Union[dict[str, Any], str, None] = None,
        order_by: Optional[list[str]] = None,
    ) -> Sequence[read_schemas.ClimaticIndicatorRead]:
        list_params = functools.partial(
            db.list_climatic_indicators,
            limit=limit,
            offset=skip,
            name_filter=str(where) if where not in (None, "") else None,
            include_total=False,
        )
        db_climatic_indicators, _ = await anyio.to_thread.run_sync(
            list_params, request.state.session
        )
        return [self._serialize_instance(ind) for ind in db_climatic_indicators]
