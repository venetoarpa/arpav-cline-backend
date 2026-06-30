from .analytics import (
    collect_all_forecast_coverage_download_requests,  # noqa
    collect_all_historical_coverage_download_requests,  # noqa
    collect_all_time_series_download_requests,  # noqa
    create_forecast_coverage_download_request,  # noqa
    create_historical_coverage_download_request,  # noqa
    create_time_series_download_request,  # noqa
    delete_forecast_coverage_download_request,  # noqa
    delete_historical_coverage_download_request,  # noqa
    delete_time_series_download_request,  # noqa
    get_forecast_coverage_download_request,  # noqa
    get_historical_coverage_download_request,  # noqa
    get_time_series_download_request,  # noqa
    list_forecast_coverage_download_requests,  # noqa
    list_historical_coverage_download_requests,  # noqa
    list_time_series_download_requests,  # noqa
)

from .climaticindicators import (
    collect_all_climatic_indicators,  # noqa
    create_climatic_indicator,  # noqa
    delete_climatic_indicator,  # noqa
    get_climatic_indicator,  # noqa
    get_climatic_indicator_by_identifier,  # noqa
    list_climatic_indicators,  # noqa
    update_climatic_indicator,  # noqa
)

from .forecastcoverages import (
    collect_all_forecast_coverages,  # noqa
    collect_all_forecast_coverage_configurations,  # noqa
    collect_all_forecast_coverage_configurations_with_identifier_filter,  # noqa
    collect_all_forecast_models,  # noqa
    collect_all_forecast_model_groups,  # noqa
    collect_all_forecast_time_windows,  # noqa
    collect_all_forecast_year_period_groups,  # noqa
    create_forecast_coverage_configuration,  # noqa
    create_forecast_model,  # noqa
    create_forecast_model_group,  # noqa
    create_forecast_time_window,  # noqa
    create_forecast_year_period_group,  # noqa
    delete_forecast_coverage_configuration,  # noqa
    delete_forecast_model,  # noqa
    delete_forecast_model_group,  # noqa
    delete_forecast_time_window,  # noqa
    delete_forecast_year_period_group,  # noqa
    generate_forecast_coverages_for_other_models,  # noqa
    generate_forecast_coverages_from_configuration,  # noqa
    get_forecast_coverage,  # noqa
    get_forecast_coverage_configuration,  # noqa
    get_forecast_coverage_configuration_by_identifier,  # noqa
    # get_forecast_coverage_data_series,  # noqa
    get_forecast_model,  # noqa
    get_forecast_model_by_name,  # noqa
    get_forecast_model_group,  # noqa
    get_forecast_model_group_by_name,  # noqa
    get_forecast_time_window,  # noqa
    get_forecast_time_window_by_name,  # noqa
    get_forecast_year_period_group,  # noqa
    get_forecast_year_period_group_by_name,  # noqa
    legacy_collect_all_forecast_coverage_configurations,  # noqa
    legacy_list_forecast_coverage_configurations,  # noqa
    legacy_list_forecast_coverages,  # noqa
    list_forecast_coverages,  # noqa
    list_forecast_coverage_configurations,  # noqa
    list_forecast_models,  # noqa
    list_forecast_model_groups,  # noqa
    list_forecast_time_windows,  # noqa
    list_forecast_year_period_groups,  # noqa
    update_forecast_coverage_configuration,  # noqa
    update_forecast_model,  # noqa
    update_forecast_model_group,  # noqa
    update_forecast_time_window,  # noqa
    update_forecast_year_period_group,  # noqa
)

from .historicalcoverages import (
    collect_all_historical_coverages,  # noqa
    collect_all_historical_coverage_configurations,  # noqa
    collect_all_historical_coverage_configurations_with_identifier_filter,  # noqa
    collect_all_historical_year_period_groups,  # noqa
    create_historical_coverage_configuration,  # noqa
    create_historical_year_period_group,  # noqa
    delete_historical_coverage_configuration,  # noqa
    delete_historical_year_period_group,  # noqa
    generate_historical_coverages_from_configuration,  # noqa
    get_historical_coverage,  # noqa
    get_historical_coverage_configuration,  # noqa
    get_historical_coverage_configuration_by_identifier,  # noqa
    get_historical_year_period_group,  # noqa
    get_historical_year_period_group_by_name,  # noqa
    legacy_collect_all_historical_coverage_configurations,  # noqa
    legacy_list_historical_coverage_configurations,  # noqa
    legacy_list_historical_coverages,  # noqa
    list_historical_coverages,  # noqa
    list_historical_coverage_configurations,  # noqa
    list_historical_year_period_groups,  # noqa
    update_historical_coverage_configuration,  # noqa
    update_historical_year_period_group,  # noqa
)

from .legacy import legacy_list_configuration_parameters  # noqa

from .municipalities import (
    collect_all_municipalities,  # noqa
    create_many_municipalities,  # noqa
    delete_all_municipalities,  # noqa
    list_municipalities,  # noqa
    list_municipality_centroids,  # noqa
)

from .observationseries import (
    collect_all_observation_measurements,  # noqa
    collect_all_observation_series_configurations,  # noqa
    create_many_observation_measurements,  # noqa
    create_observation_measurement,  # noqa
    create_observation_series_configuration,  # noqa
    delete_observation_measurement,  # noqa
    delete_observation_series_configuration,  # noqa
    find_new_station_measurements,  # noqa
    get_observation_measurement,  # noqa
    get_observation_series_configuration,  # noqa
    get_observation_series_configuration_by_identifier,  # noqa
    list_observation_measurements,  # noqa
    list_observation_series_configurations,  # noqa
    update_observation_series_configuration,  # noqa
)

from .observationstations import (
    collect_all_observation_stations,  # noqa
    create_many_observation_stations,  # noqa
    create_observation_station,  # noqa
    delete_observation_station,  # noqa
    get_observation_station,  # noqa
    get_observation_station_by_code,  # noqa
    get_observation_station_by_name,  # noqa
    list_observation_stations,  # noqa
    update_observation_station,  # noqa
)

from .overviews import (
    list_forecast_overview_series_configurations,  # noqa
    collect_all_forecast_overview_series_configurations,  # noqa
    get_forecast_overview_series_configuration,  # noqa
    get_forecast_overview_series_configuration_by_identifier,  # noqa
    create_forecast_overview_series_configuration,  # noqa
    update_forecast_overview_series_configuration,  # noqa
    delete_forecast_overview_series_configuration,  # noqa
    list_observation_overview_series_configurations,  # noqa
    collect_all_observation_overview_series_configurations,  # noqa
    get_observation_overview_series_configuration,  # noqa
    get_observation_overview_series_configuration_by_identifier,  # noqa
    create_observation_overview_series_configuration,  # noqa
    update_observation_overview_series_configuration,  # noqa
    delete_observation_overview_series_configuration,  # noqa
    generate_forecast_overview_series_from_configuration,  # noqa
    generate_observation_overview_series_from_configuration,  # noqa
)

from .spatialregions import (
    collect_all_spatial_regions,  # noqa
    create_spatial_region,  # noqa
    delete_spatial_region,  # noqa
    get_spatial_region,  # noqa
    get_spatial_region_by_name,  # noqa
    list_spatial_regions,  # noqa
    update_spatial_region,  # noqa
)

from .engine import get_engine  # noqa
