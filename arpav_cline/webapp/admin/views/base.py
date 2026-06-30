import functools
import logging
from typing import (
    Any,
    Optional,
    Sequence,
    Union,
)

import anyio.to_thread
import shapely.io
import starlette_admin
from starlette.requests import Request
from starlette_admin.contrib.sqlmodel import ModelView

from .... import db
from ....schemas import base
from .. import schemas as read_schemas

logger = logging.getLogger(__name__)


class SpatialRegionView(ModelView):
    identity = "spatial_regions"
    name = "Spatial Region"
    label = "Spatial Regions"
    pk_attr = "id"

    exclude_fields_from_list = (
        "id",
        "geom",
        "display_name_english",
        "display_name_italian",
    )
    exclude_fields_from_detail = ("id",)

    fields = (
        starlette_admin.IntegerField("id"),
        starlette_admin.StringField("name", required=True),
        starlette_admin.StringField("display_name_english", required=True),
        starlette_admin.StringField("display_name_italian", required=True),
        starlette_admin.IntegerField("sort_order"),
        starlette_admin.JSONField("geom", required=True),
    )
    search_builder = False

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.icon = "fa-solid fa-globe"

    def can_create(self, request: Request) -> bool:
        return False

    def can_edit(self, request: Request) -> bool:
        return False

    @staticmethod
    def _serialize_instance(instance: base.SpatialRegion):
        geom = shapely.io.from_wkb(bytes(instance.geom.data))
        return read_schemas.SpatialRegionRead(
            **instance.model_dump(exclude={"geom"}),
            geom=shapely.io.to_geojson(geom, indent=2),
        )

    async def find_by_pk(
        self, request: Request, pk: int
    ) -> read_schemas.SpatialRegionRead:
        db_spatial_region = await anyio.to_thread.run_sync(
            db.get_spatial_region, request.state.session, pk
        )
        return self._serialize_instance(db_spatial_region)

    async def find_all(
        self,
        request: Request,
        skip: int = 0,
        limit: int = 100,
        where: Union[dict[str, Any], str, None] = None,
        order_by: Optional[list[str]] = None,
    ) -> Sequence[read_schemas.SpatialRegionRead]:
        list_params = functools.partial(
            db.list_spatial_regions,
            limit=limit,
            offset=skip,
            include_total=False,
        )
        db_spatial_regions, _ = await anyio.to_thread.run_sync(
            list_params, request.state.session
        )
        return [self._serialize_instance(sr) for sr in db_spatial_regions]
