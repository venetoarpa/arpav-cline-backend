import logging
import typing

from pathlib import Path

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.exceptions import HTTPException
from starlette_admin.contrib.sqlmodel import Admin
from starlette_admin.views import (
    DropDown,
    Link,
)

from ...db import get_engine
from ...schemas.analytics import (
    ForecastCoverageDownloadRequest,
    HistoricalCoverageDownloadRequest,
    TimeSeriesDownloadRequest,
)
from ...schemas.base import SpatialRegion
from ...schemas.climaticindicators import ClimaticIndicator
from ...schemas.coverages import (
    ForecastCoverageConfiguration,
    ForecastModel,
    ForecastModelGroup,
    ForecastTimeWindow,
    ForecastYearPeriodGroup,
    HistoricalCoverageConfiguration,
    HistoricalYearPeriodGroup,
)
from ...schemas.observations import (
    ObservationMeasurement,
    ObservationSeriesConfiguration,
    ObservationStation,
)
from ...schemas.overviews import (
    ForecastOverviewSeriesConfiguration,
    ObservationOverviewSeriesConfiguration,
)
from . import auth
from .middlewares import SqlModelDbSessionMiddleware
from .views import (
    analytics as analytics_views,
    base as base_views,
    climaticindicators as climaticindicators_views,
    coverages as coverage_views,
    observations as observations_views,
    overviews as overviews_views,
)

if typing.TYPE_CHECKING:
    from ...config import ArpavPpcvSettings

logger = logging.getLogger(__name__)


class ArpavPpcvAdmin(Admin):
    def mount_to(self, app: Starlette, settings: "ArpavPpcvSettings") -> None:
        """Reimplemented in order to pass settings to the admin app."""
        admin_app = Starlette(
            routes=self.routes,
            middleware=self.middlewares,
            debug=self.debug,
            exception_handlers={HTTPException: self._render_error},
        )
        admin_app.state.ROUTE_NAME = self.route_name
        admin_app.state.settings = settings
        app.mount(
            self.base_url,
            app=admin_app,
            name=self.route_name,
        )


def create_admin(settings: "ArpavPpcvSettings") -> ArpavPpcvAdmin:
    engine = get_engine(settings)
    admin = ArpavPpcvAdmin(
        engine,
        debug=settings.debug,
        templates_dir=str(settings.templates_dir / "admin"),
        statics_dir=str(Path(__file__).parent / "statics"),
        auth_provider=auth.UsernameAndPasswordProvider(),
        middlewares=[
            Middleware(SessionMiddleware, secret_key=settings.session_secret_key),
            Middleware(SqlModelDbSessionMiddleware, engine=engine),
        ],
    )
    admin.add_view(climaticindicators_views.ClimaticIndicatorView(ClimaticIndicator))
    admin.add_view(base_views.SpatialRegionView(SpatialRegion))
    admin.add_view(
        DropDown(
            "Overviews",
            icon="fa-regular fa-flag",
            always_open=False,
            views=[
                overviews_views.ForecastOverviewSeriesConfigurationView(
                    ForecastOverviewSeriesConfiguration
                ),
                overviews_views.ObservationOverviewSeriesConfigurationView(
                    ObservationOverviewSeriesConfiguration
                ),
            ],
        )
    )
    admin.add_view(
        DropDown(
            "Forecasts",
            icon="fa-solid fa-chart-line",
            always_open=False,
            views=[
                coverage_views.ForecastCoverageConfigurationView(
                    ForecastCoverageConfiguration
                ),
                coverage_views.ForecastYearPeriodGroupView(ForecastYearPeriodGroup),
                coverage_views.ForecastModelView(ForecastModel),
                coverage_views.ForecastModelGroupView(ForecastModelGroup),
                coverage_views.ForecastTimeWindowView(ForecastTimeWindow),
            ],
        )
    )
    admin.add_view(
        DropDown(
            "Historical",
            icon="fa-solid fa-clock-rotate-left",
            always_open=False,
            views=[
                coverage_views.HistoricalCoverageConfigurationView(
                    HistoricalCoverageConfiguration
                ),
                coverage_views.HistoricalYearPeriodGroupView(HistoricalYearPeriodGroup),
            ],
        )
    )
    admin.add_view(
        DropDown(
            "Observations",
            icon="fa-solid fa-ruler",
            always_open=False,
            views=[
                observations_views.ObservationMeasurementView(ObservationMeasurement),
                observations_views.ObservationSeriesConfigurationView(
                    ObservationSeriesConfiguration
                ),
                observations_views.ObservationStationView(ObservationStation),
            ],
        )
    )
    admin.add_view(
        DropDown(
            "Download stats",
            icon="fa-solid fa-chart-pie",
            always_open=False,
            views=[
                analytics_views.ForecastCoverageDownloadRequestView(
                    ForecastCoverageDownloadRequest
                ),
                analytics_views.HistoricalCoverageDownloadRequestView(
                    HistoricalCoverageDownloadRequest
                ),
                analytics_views.TimeSeriesDownloadRequestView(
                    TimeSeriesDownloadRequest
                ),
            ],
        )
    )
    admin.add_view(
        Link(
            "V2 API docs",
            icon="fa fa-link",
            url=f"{settings.public_url}{settings.v2_api_mount_prefix}/docs",
            target="blank_",
        )
    )
    admin.add_view(
        Link(
            "Public site",
            icon="fa fa-link",
            url=f"{settings.public_url}",
            target="blank_",
        )
    )
    return admin
