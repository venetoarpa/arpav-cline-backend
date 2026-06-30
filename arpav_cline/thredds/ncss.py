"""Utilities for interacting with the THREDDS NetCDF Subset Service (NCSS).

Get more detail about NCSS at:

https://docs.unidata.ucar.edu/tds/current/userguide/netcdf_subset_service_ref.html

"""
import dataclasses
import datetime as dt
import io
import logging
import xml.etree.ElementTree as etree
from typing import (
    Optional,
    TYPE_CHECKING,
    Union,
)

import httpx
import pandas as pd
import shapely
from pandas.core.indexes.datetimes import DatetimeIndex

from ..exceptions import CoverageDataRetrievalError
from . import models

if TYPE_CHECKING:
    from ..config import ThreddsServerSettings
    from ..schemas.static import (
        StaticForecastCoverage,
        StaticHistoricalCoverage,
    )

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class SimpleCoverageDataRetriever:
    settings: "ThreddsServerSettings"
    http_client: httpx.Client
    static_coverage: Union["StaticForecastCoverage", "StaticHistoricalCoverage"]

    def retrieve_main_data(
        self,
        location: shapely.Point,
        temporal_range: Optional[tuple[dt.date | None, dt.date | None]] = None,
        target_series_name: Optional[str] = None,
    ) -> Optional[pd.Series]:
        if all(
            (
                self.static_coverage.ncss_url,
                self.static_coverage.netcdf_variable_name,
            )
        ):
            return self._retrieve_location_data(
                self.static_coverage.ncss_url,
                self.static_coverage.netcdf_variable_name,
                location,
                temporal_range,
                target_series_name=target_series_name
                or self.static_coverage.coverage_identifier,
            )
        else:
            return None

    def _retrieve_location_data(
        self,
        ncss_url: str,
        netcdf_variable_name: str,
        location: shapely.Point,
        temporal_range: Optional[tuple[dt.date | None, dt.date | None]] = None,
        target_series_name: Optional[str] = None,
    ) -> Optional[pd.Series]:
        result = None
        raw_data = query_dataset(
            self.http_client,
            thredds_ncss_url=ncss_url,
            variable_name=netcdf_variable_name,
            longitude=location.x,
            latitude=location.y,
            time_start=temporal_range[0],
            time_end=temporal_range[1],
        )
        logger.debug(f"{raw_data=}")
        if raw_data:
            result = _parse_ncss_dataset(
                raw_data,
                netcdf_variable_name,
                time_start=temporal_range[0] if temporal_range else None,
                time_end=temporal_range[1] if temporal_range else None,
                target_series_name=target_series_name,
            )
        else:
            logger.info(f"Did not receive any data from {ncss_url!r}")
        return result


@dataclasses.dataclass
class ForecastCoverageDataRetriever(SimpleCoverageDataRetriever):
    static_coverage: "StaticForecastCoverage"

    def retrieve_lower_uncertainty_data(
        self,
        location: shapely.Point,
        temporal_range: Optional[tuple[dt.date | None, dt.date | None]] = None,
        target_series_name: Optional[str] = None,
    ) -> Optional[pd.Series]:
        identifier = (
            target_series_name or self.static_coverage.lower_uncertainty_identifier
        )
        result = None
        if all(
            (
                identifier,
                self.static_coverage.lower_uncertainty_ncss_url,
                self.static_coverage.lower_uncertainy_netcdf_variable_name,
            )
        ):
            result = self._retrieve_location_data(
                self.static_coverage.lower_uncertainty_ncss_url,
                self.static_coverage.lower_uncertainy_netcdf_variable_name,
                location,
                temporal_range,
                target_series_name=identifier,
            )
        return result

    def retrieve_upper_uncertainty_data(
        self,
        location: shapely.Point,
        temporal_range: Optional[tuple[dt.date | None, dt.date | None]] = None,
        target_series_name: Optional[str] = None,
    ) -> Optional[pd.Series]:
        identifier = (
            target_series_name or self.static_coverage.upper_uncertainty_identifier
        )
        if all(
            (
                identifier,
                self.static_coverage.upper_uncertainty_ncss_url,
                self.static_coverage.upper_uncertainy_netcdf_variable_name,
            )
        ):
            return self._retrieve_location_data(
                self.static_coverage.upper_uncertainty_ncss_url,
                self.static_coverage.upper_uncertainy_netcdf_variable_name,
                location,
                temporal_range,
                target_series_name=identifier,
            )
        else:
            return None


def _parse_ncss_dataset(
    raw_data: str,
    source_main_ds_name: str,
    time_start: dt.datetime | None,
    time_end: dt.datetime | None,
    target_series_name: str | None = None,
) -> Optional[pd.Series]:
    df = pd.read_csv(io.StringIO(raw_data), parse_dates=["time"])
    try:
        col_name = [c for c in df.columns if c.startswith(f"{source_main_ds_name}[")][0]
    except IndexError:
        raise RuntimeError(
            f"Could not extract main data series from dataframe "
            f"with columns {df.columns}"
        )
    else:
        # keep only time and main variable - we don't care about other stuff
        df = df[["time", col_name]]
        if target_series_name is not None:
            df = df.rename(columns={col_name: target_series_name})

        # - filter out values outside the temporal range
        df.set_index("time", inplace=True)

        # check that we got a datetime index, otherwise we need to modify the values
        if type(df.index) is not DatetimeIndex:
            new_index = pd.to_datetime(df.index.map(_simplify_date))
            df.index = new_index

        if time_start is not None:
            df = df[time_start:]
        if time_end is not None:
            df = df[:time_end]
        result = df[target_series_name]
        result.dropna(inplace=True)
        return result if result.size > 0 else None


def _simplify_date(raw_date: str) -> str:
    """Simplify a date by loosing its day and time information.

    This will reset a date to the 15th day of the underlying month.
    """
    raw_year, raw_month = raw_date.split("-")[:2]
    return f"{raw_year}-{raw_month}-15T00:00:00+00:00"


async def async_get_dataset_description(
    http_client: httpx.AsyncClient,
    thredds_ncss_url: str,
) -> models.ThreddsDatasetDescription:
    response = await http_client.get(f"{thredds_ncss_url}/dataset.xml")
    response.raise_for_status()
    root = etree.fromstring(response.text)
    logger.debug("info response:")
    logger.debug(etree.tostring(root).decode("utf-8"))
    variables = []
    for var_info in root.findall("./gridSet/grid"):
        variables.append(
            models.ThreddsDatasetDescriptionVariable(
                name=var_info.get("name"),
                description=var_info.get("desc"),
                units=var_info.findall("./*[@name='units']")[0].get("value"),
            )
        )
    time_span_el = root.findall("./TimeSpan")[0]
    declared_start = time_span_el.findall("./begin")[0].text.replace("Z", "")
    try:
        start = dt.datetime.fromisoformat(declared_start)
    except ValueError:
        logger.warning(
            f"THREDDS reported a start date of {declared_start!r} - this cannot be "
            f"parsed into a datetime instance so it was ignored"
        )
        start = None
    declared_end = time_span_el.findall("./end")[0].text.replace("Z", "")
    try:
        end = dt.datetime.fromisoformat(declared_end)
    except ValueError:
        logger.warning(
            f"THREDDS reported an end date of {declared_end!r} - this cannot be parsed "
            f"into a datetime instance so it was ignored"
        )
        end = None

    temporal_bounds = models.ThreddsDatasetDescriptionTemporalBounds(
        start=start,
        end=end,
    )
    lat_lon_el = root.findall("./LatLonBox")[0]
    spatial_bounds = shapely.box(
        xmin=float(lat_lon_el.findall("./west")[0].text),
        ymin=float(lat_lon_el.findall("./south")[0].text),
        xmax=float(lat_lon_el.findall("./east")[0].text),
        ymax=float(lat_lon_el.findall("./north")[0].text),
    )
    return models.ThreddsDatasetDescription(
        variables=variables,
        spatial_bounds=spatial_bounds,
        temporal_bounds=temporal_bounds,
    )


def get_dataset_description(
    http_client: httpx.Client,
    thredds_ncss_url: str,
) -> models.ThreddsDatasetDescription:
    response = http_client.get(f"{thredds_ncss_url}/dataset.xml")
    response.raise_for_status()
    root = etree.fromstring(response.text)
    variables = []
    for var_info in root.findall("./gridSet/grid"):
        variables.append(
            models.ThreddsDatasetDescriptionVariable(
                name=var_info.get("name"),
                description=var_info.get("desc"),
                units=var_info.findall("./*[@name='units']")[0].get("value"),
            )
        )
    time_span_el = root.findall("./TimeSpan")[0]
    temporal_bounds = models.ThreddsDatasetDescriptionTemporalBounds(
        start=dt.datetime.fromisoformat(time_span_el.findall("./begin")[0].text),
        end=dt.datetime.fromisoformat(time_span_el.findall("./end")[0].text),
    )
    lat_lon_el = root.findall("./LatLonBox")[0]
    spatial_bounds = shapely.box(
        xmin=float(lat_lon_el.findall("./west")[0].text),
        ymin=float(lat_lon_el.findall("./south")[0].text),
        xmax=float(lat_lon_el.findall("./east")[0].text),
        ymax=float(lat_lon_el.findall("./north")[0].text),
    )
    return models.ThreddsDatasetDescription(
        variables=variables,
        spatial_bounds=spatial_bounds,
        temporal_bounds=temporal_bounds,
    )


async def async_query_dataset_area(
    http_client: httpx.AsyncClient,
    thredds_ncss_url: str,
    netcdf_variable_names: list[str] | None = None,
    bbox: shapely.Polygon | None = None,
    temporal_range: tuple[dt.datetime | None, dt.datetime | None] | None = None,
):
    """Query THREDDS for the specified variables, spatial and temporal extents."""
    time_start = temporal_range[0]
    time_end = temporal_range[1]
    need_info = (
        len(netcdf_vars := netcdf_variable_names or []) == 0
        or (time_start is None and time_end is not None)
        or (time_end is None and time_start is not None)
    )
    if need_info:
        info = await async_get_dataset_description(http_client, thredds_ncss_url)
        netcdf_vars = (
            [v.name for v in info.variables] if len(netcdf_vars) == 0 else netcdf_vars
        )
        time_start = info.temporal_bounds.start if time_start is None else time_start
        time_end = info.temporal_bounds.end if time_end is None else time_end

    temporal_parameters = {}
    if time_start is None and time_end is None:
        temporal_parameters["time"] = "all"
    else:
        temporal_parameters.update(
            {
                "time_start": time_start.isoformat(),
                "time_end": time_end.isoformat(),
            }
        )
    spatial_parameters = {}
    if bbox is not None:
        min_x, min_y, max_x, max_y = bbox.bounds
        spatial_parameters.update(
            {
                "north": max_y,
                "south": min_y,
                "east": max_x,
                "west": min_x,
            }
        )
    ncss_params = {
        "accept": "netCDF4",
        "var": ",".join(netcdf_vars),
        **temporal_parameters,
        **spatial_parameters,
    }
    request = http_client.build_request("GET", thredds_ncss_url, params=ncss_params)
    return await http_client.send(request, stream=True)


async def async_query_dataset(
    http_client: httpx.AsyncClient,
    thredds_ncss_url: str,
    netcdf_variable_name: str,
    longitude: float,
    latitude: float,
    time_start: dt.datetime | None = None,
    time_end: dt.datetime | None = None,
):
    """Query THREDDS for the specified variable."""
    if time_start is None or time_end is None:
        temporal_parameters = {
            "time": "all",
        }
    else:
        temporal_parameters = {
            "time_start": time_start.isoformat(),
            "time_end": time_end.isoformat(),
        }
    response = await http_client.get(
        thredds_ncss_url,
        params={
            "var": netcdf_variable_name,
            "latitude": latitude,
            "longitude": longitude,
            "accept": "CSV",
            **temporal_parameters,
        },
    )
    try:
        response.raise_for_status()
    except httpx.HTTPError as err:
        logger.exception(msg="Could not retrieve data")
        logger.debug(f"upstream NCSS error: {response.content}")
        raise CoverageDataRetrievalError() from err
    else:
        result = response.text
    return result


def query_dataset(
    http_client: httpx.Client,
    thredds_ncss_url: str,
    variable_name: str,
    longitude: float,
    latitude: float,
    time_start: dt.datetime | None = None,
    time_end: dt.datetime | None = None,
) -> str | None:
    """Query THREDDS for the specified variable."""
    if time_start is None or time_end is None:
        temporal_parameters = {
            "time": "all",
        }
    else:
        temporal_parameters = {
            "time_start": time_start.isoformat(),
            "time_end": time_end.isoformat(),
        }
    response = http_client.get(
        thredds_ncss_url,
        params={
            "var": variable_name,
            "latitude": latitude,
            "longitude": longitude,
            "accept": "CSV",
            **temporal_parameters,
        },
    )
    try:
        response.raise_for_status()
    except httpx.HTTPError:
        logger.exception(msg="Could not retrieve data")
        logger.debug(f"upstream NCSS error: {response.content}")
        result = None
    else:
        result = response.text
    return result
