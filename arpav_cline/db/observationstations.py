import logging
from typing import (
    Optional,
    Sequence,
)

import shapely
import sqlalchemy
import sqlmodel
from geoalchemy2.shape import from_shape
from sqlalchemy import func

from ..schemas.observations import (
    ObservationStation,
    ObservationStationCreate,
    ObservationStationUpdate,
    ObservationStationClimaticIndicatorLink,
)
from ..schemas.static import (
    ObservationStationManager,
)

from .base import (
    add_substring_filter,
    get_total_num_records,
)
from .climaticindicators import get_climatic_indicator

logger = logging.getLogger(__name__)


def get_observation_station(
    session: sqlmodel.Session, observation_station_id: int
) -> Optional[ObservationStation]:
    return session.get(ObservationStation, observation_station_id)


def get_observation_station_by_name(
    session: sqlmodel.Session, name: str
) -> Optional[ObservationStation]:
    return session.exec(
        sqlmodel.select(ObservationStation).where(ObservationStation.name == name)  # noqa
    ).first()


def get_observation_station_by_code(
    session: sqlmodel.Session, code: str
) -> Optional[ObservationStation]:
    """Get an observation station by its code"""
    return session.exec(
        sqlmodel.select(ObservationStation).where(ObservationStation.code == code)  # noqa
    ).first()


def list_observation_stations(
    session: sqlmodel.Session,
    *,
    limit: int = 20,
    offset: int = 0,
    include_total: bool = False,
    name_filter: Optional[str] = None,
    polygon_intersection_filter: Optional[shapely.Polygon] = None,
    manager_filter: Optional[ObservationStationManager] = None,
    climatic_indicator_id_filter: Optional[int] = None,
) -> tuple[Sequence[ObservationStation], Optional[int]]:
    """List existing observation stations.

    The ``polygon_intersection_filter`` parameter is expected to be a polygon
    geometry in the EPSG:4326 CRS.
    """
    statement = sqlmodel.select(ObservationStation).order_by(
        ObservationStation.code  # noqa
    )
    if name_filter is not None:
        statement = add_substring_filter(
            statement,
            name_filter,
            ObservationStation.name,  # noqa
        )
    if polygon_intersection_filter is not None:
        statement = statement.where(
            func.ST_Intersects(
                ObservationStation.geom,  # noqa
                func.ST_GeomFromWKB(
                    shapely.io.to_wkb(polygon_intersection_filter), 4326
                ),
            )
        )
    if manager_filter is not None:
        statement = statement.where(
            ObservationStation.managed_by == manager_filter  # noqa
        )
    if climatic_indicator_id_filter is not None:
        statement = statement.join(
            ObservationStationClimaticIndicatorLink,
            ObservationStation.id  # noqa
            == ObservationStationClimaticIndicatorLink.observation_station_id,  # noqa
        ).where(
            ObservationStationClimaticIndicatorLink.climatic_indicator_id  # noqa
            == climatic_indicator_id_filter,
        )
    items = session.exec(statement.offset(offset).limit(limit)).all()
    num_items = get_total_num_records(session, statement) if include_total else None
    return items, num_items


def collect_all_observation_stations(
    session: sqlmodel.Session,
    polygon_intersection_filter: Optional[shapely.Polygon] = None,
    manager_filter: Optional[ObservationStationManager] = None,
    climatic_indicator_id_filter: Optional[int] = None,
) -> Sequence[ObservationStation]:
    """Collect all observation stations.

    The ``polygon_intersection_filter`` parameter is expected to be a polygon
    geometry in the EPSG:4326 CRS.
    """
    _, num_total = list_observation_stations(
        session,
        limit=1,
        include_total=True,
        polygon_intersection_filter=polygon_intersection_filter,
        manager_filter=manager_filter,
        climatic_indicator_id_filter=climatic_indicator_id_filter,
    )
    result, _ = list_observation_stations(
        session,
        limit=num_total,
        include_total=False,
        polygon_intersection_filter=polygon_intersection_filter,
        manager_filter=manager_filter,
        climatic_indicator_id_filter=climatic_indicator_id_filter,
    )
    return result


def create_observation_station(
    session: sqlmodel.Session,
    observation_station_create: ObservationStationCreate,
) -> ObservationStation:
    """Create a new observation station."""
    geom = shapely.io.from_geojson(observation_station_create.geom.model_dump_json())
    wkbelement = from_shape(geom)
    db_item = ObservationStation(
        **observation_station_create.model_dump(
            exclude={
                "geom",
                "climatic_indicators",
            }
        ),
        geom=wkbelement,
    )
    session.add(db_item)
    for climatic_indicator_id in observation_station_create.climatic_indicators or []:
        climatic_indicator = get_climatic_indicator(session, climatic_indicator_id)
        if climatic_indicator is not None:
            db_item.climatic_indicators.append(climatic_indicator)
        else:
            logger.warning(
                f"climatic indicator {climatic_indicator_id} not found, ignoring..."
            )
    try:
        session.commit()
    except sqlalchemy.exc.DBAPIError:
        raise
    else:
        session.refresh(db_item)
        return db_item


def create_many_observation_stations(
    session: sqlmodel.Session,
    stations_to_create: Sequence[ObservationStationCreate],
) -> list[ObservationStation]:
    """Create several observation stations."""
    db_records = []
    for item_create in stations_to_create:
        geom = shapely.io.from_geojson(item_create.geom.model_dump_json())
        wkbelement = from_shape(geom)
        db_item = ObservationStation(
            **item_create.model_dump(
                exclude={
                    "geom",
                    "climatic_indicators",
                }
            ),
            geom=wkbelement,
        )
        db_records.append(db_item)
        session.add(db_item)
        for climatic_indicator_id in item_create.climatic_indicators or []:
            climatic_indicator = get_climatic_indicator(session, climatic_indicator_id)
            if climatic_indicator is not None:
                db_item.climatic_indicators.append(climatic_indicator)
            else:
                logger.warning(
                    f"climatic indicator {climatic_indicator_id} not found, ignoring..."
                )
    try:
        session.commit()
    except sqlalchemy.exc.DBAPIError:
        raise
    else:
        for db_record in db_records:
            session.refresh(db_record)
        return db_records


def update_observation_station(
    session: sqlmodel.Session,
    db_observation_station: ObservationStation,
    observation_station_update: ObservationStationUpdate,
) -> ObservationStation:
    """Update an observation station."""
    if observation_station_update.geom is not None:
        geom = from_shape(
            shapely.io.from_geojson(observation_station_update.geom.model_dump_json())
        )
    else:
        geom = None
    other_data = observation_station_update.model_dump(
        exclude={
            "geom",
            "climatic_indicators",
        },
        exclude_unset=True,
    )
    data = {**other_data}
    if geom is not None:
        data["geom"] = geom
    for key, value in data.items():
        setattr(db_observation_station, key, value)
    session.add(db_observation_station)
    updated_climatic_indicators = []
    for climatic_indicator_id in observation_station_update.climatic_indicators or []:
        climatic_indicator = get_climatic_indicator(session, climatic_indicator_id)
        if climatic_indicator is not None:
            updated_climatic_indicators.append(climatic_indicator)
        else:
            logger.warning(
                f"Climatic indicator with id {climatic_indicator_id} not found, "
                f"ignoring..."
            )
    db_observation_station.climatic_indicators = updated_climatic_indicators
    session.commit()
    session.refresh(db_observation_station)
    return db_observation_station


def delete_observation_station(
    session: sqlmodel.Session, observation_station_id: int
) -> None:
    """Delete an observation station."""
    db_item = get_observation_station(session, observation_station_id)
    if db_item is not None:
        session.delete(db_item)
        session.commit()
    else:
        raise RuntimeError("Observation station not found")
