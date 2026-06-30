"""Deployment script

This is used for managing semi-automated deployments of the system.
"""

# NOTE: IN ORDER TO SIMPLIFY DEPLOYMENT, THIS SCRIPT SHALL ONLY USE STUFF FROM THE
# PYTHON STANDARD LIBRARY

import argparse
import dataclasses
import configparser
import json
import logging
import os
import shlex
import shutil
import socket
import subprocess
import sys
import urllib.request
from pathlib import Path
from string import Template
from typing import Protocol
from urllib.error import HTTPError

logger = logging.getLogger(__name__)

_DO_NOT_UPDATE_FLAG_NAME = "--no-auto-update"


@dataclasses.dataclass
class DeploymentConfiguration:
    arpa_fvg_auth_token_path: Path
    backend_image: str
    compose_project_name: str = dataclasses.field(init=False)
    compose_template: str
    db_image_tag: str
    db_name: str
    db_password: str
    db_user: str
    deployment_files_repo: str
    deployment_files_repo_clone_destination: Path
    deployment_root: Path
    discord_notification_urls: list[str]
    executable_webapp_service_name: str = dataclasses.field(init=False)
    frontend_image: str
    frontend_env_arpav_backend_api_base_url: str = dataclasses.field(init=False)
    frontend_env_arpav_tolgee_base_url: str = dataclasses.field(init=False)
    martin_config_source: str
    martin_conf_path: Path = dataclasses.field(
        init=False
    )  # is copied to inside the deployment_root dir
    martin_env_database_url: str = dataclasses.field(init=False)
    martin_image_tag: str
    observation_station_blacklist: str
    observation_stations_refresher_flow_cron_schedule: str
    observation_measurements_refresher_flow_cron_schedule: str
    station_variables_refresher_flow_cron_schedule: str
    prefect_db_name: str
    prefect_db_password: str
    prefect_db_user: str
    prefect_server_env_allow_ephemeral_mode: bool = dataclasses.field(init=False)
    prefect_server_env_api_database_connection_url: str = dataclasses.field(init=False)
    prefect_server_env_api_host: str = dataclasses.field(init=False)
    prefect_server_env_api_port: int = dataclasses.field(init=False)
    prefect_server_env_api_url: str = dataclasses.field(init=False)
    prefect_server_env_cli_prompt: bool = dataclasses.field(init=False)
    prefect_server_env_csrf_protection_enabled: bool = dataclasses.field(init=False)
    prefect_server_env_debug_mode: bool = dataclasses.field(init=False)
    prefect_server_env_home: str = dataclasses.field(init=False)
    prefect_server_env_ui_api_url: str = dataclasses.field(init=False)
    prefect_server_env_ui_serve_base: str = dataclasses.field(init=False)
    prefect_server_env_ui_url: str = dataclasses.field(init=False)
    prefect_server_image_tag: str
    prefect_static_worker_env_arpav_ppcv_db_dsn: str = dataclasses.field(init=False)
    prefect_static_worker_env_arpav_ppcv_debug: bool = dataclasses.field(init=False)
    prefect_static_worker_env_prefect_api_url: str = dataclasses.field(init=False)
    prefect_static_worker_env_prefect_debug_mode: bool = dataclasses.field(init=False)
    reverse_proxy_image_tag: str
    reverse_proxy_main_domain_name: str
    reverse_proxy_tolgee_domain_name: str
    tls_cert_path: Path | None
    tls_cert_key_path: Path | None
    tolgee_app_env_server_port: int = dataclasses.field(init=False)
    tolgee_app_env_server_spring_datasource_url: str = dataclasses.field(init=False)
    tolgee_app_env_spring_datasource_password: str = dataclasses.field(init=False)
    tolgee_app_env_spring_datasource_username: str = dataclasses.field(init=False)
    tolgee_app_env_tolgee_authentication_create_demo_for_initial_user: bool = (
        dataclasses.field(init=False)
    )
    tolgee_app_env_tolgee_authentication_enabled: bool = dataclasses.field(init=False)
    tolgee_app_env_tolgee_authentication_initial_password: str
    tolgee_app_env_tolgee_authentication_jwt_secret: str
    tolgee_app_env_tolgee_file_storage_fs_data_path: str = dataclasses.field(init=False)
    tolgee_app_env_tolgee_frontend_url: str
    tolgee_app_env_tolgee_postgres_autostart_enabled: bool = dataclasses.field(
        init=False
    )
    tolgee_app_env_tolgee_telemetry_enabled: bool = dataclasses.field(init=False)
    tolgee_app_image_tag: str
    tolgee_db_name: str
    tolgee_db_password: str
    tolgee_db_user: str
    traefik_config_source: str
    traefik_file_provider_source: str | None
    traefik_conf_path: Path = dataclasses.field(
        init=False
    )  # is copied to inside the deployment_root dir
    traefik_file_provider_conf_path: Path = dataclasses.field(
        init=False
    )  # is copied to inside the deployment root dir
    traefik_users_file_path: Path
    webapp_env_admin_user_password: str
    webapp_env_admin_user_username: str
    webapp_env_allow_cors_credentials: bool = dataclasses.field(init=False)
    webapp_env_bind_host: str = dataclasses.field(init=False)
    webapp_env_bind_port: int = dataclasses.field(init=False)
    webapp_env_cors_methods: list[str] = dataclasses.field(init=False)
    webapp_env_cors_origins: list[str]
    webapp_env_db_dsn: str = dataclasses.field(init=False)
    webapp_env_db_pool_size: int
    webapp_env_debug: bool = dataclasses.field(init=False)
    webapp_env_http_client_timeout_seconds: float
    webapp_env_num_uvicorn_worker_processes: int
    webapp_env_public_url: str
    webapp_env_session_secret_key: str
    webapp_env_thredds_server_base_url: str
    webapp_env_uvicorn_log_config_file: Path
    webapp_env_vector_tile_server_base_url: str

    def __post_init__(self):
        _debug = False
        self.compose_project_name = "arpav-cline"
        self.executable_webapp_service_name = "arpav-cline-webapp-1"
        self.frontend_env_arpav_backend_api_base_url = self.webapp_env_public_url
        self.frontend_env_arpav_tolgee_base_url = (
            self.tolgee_app_env_tolgee_frontend_url
        )
        self.martin_conf_path = self.deployment_root / "martin-config.yaml"
        self.traefik_conf_path = self.deployment_root / "traefik-config.toml"
        self.traefik_file_provider_conf_path = (
            self.deployment_root / "traefik-file-provider-config.toml"
        )
        self.martin_env_database_url = (
            f"postgresql://{self.db_user}:{self.db_password}@db:5432/{self.db_name}"
        )
        self.prefect_server_env_api_database_connection_url = (
            f"postgresql+asyncpg://{self.prefect_db_user}:{self.prefect_db_password}@"
            f"prefect-db/{self.prefect_db_name}"
        )
        self.prefect_server_env_api_host = "0.0.0.0"
        self.prefect_server_env_api_port = 4200
        self.prefect_server_env_allow_ephemeral_mode = False
        self.prefect_server_env_api_url = (
            f"http://{self.prefect_server_env_api_host}:"
            f"{self.prefect_server_env_api_port}/api"
        )
        self.prefect_server_env_cli_prompt = False
        self.prefect_server_env_csrf_protection_enabled = True
        self.prefect_server_env_debug_mode = _debug
        self.prefect_server_env_home = "/prefect_home"
        self.prefect_server_env_ui_api_url = f"{self.webapp_env_public_url}/prefect/api"
        self.prefect_server_env_ui_serve_base = "/prefect/ui"
        self.prefect_server_env_ui_url = (
            f"{self.webapp_env_public_url}{self.prefect_server_env_ui_serve_base}"
        )
        self.prefect_static_worker_env_arpav_ppcv_db_dsn = (
            f"postgresql://{self.db_user}:{self.db_password}@db:5432/{self.db_name}"
        )
        self.prefect_static_worker_env_arpav_ppcv_debug = _debug
        self.prefect_static_worker_env_prefect_api_url = (
            f"http://prefect-server:{self.prefect_server_env_api_port}/api"
        )
        self.prefect_static_worker_env_prefect_debug_mode = _debug
        self.tolgee_app_env_server_port = 8080
        self.tolgee_app_env_server_spring_datasource_url = (
            f"jdbc:postgresql://tolgee-db:5432/{self.tolgee_db_name}"
        )
        self.tolgee_app_env_spring_datasource_password = self.tolgee_db_password
        self.tolgee_app_env_spring_datasource_username = self.tolgee_db_user
        self.tolgee_app_env_tolgee_authentication_create_demo_for_initial_user = False
        self.tolgee_app_env_tolgee_authentication_enabled = True
        self.tolgee_app_env_tolgee_file_storage_fs_data_path = "/data"
        self.tolgee_app_env_tolgee_postgres_autostart_enabled = False
        self.tolgee_app_env_tolgee_telemetry_enabled = False
        self.webapp_env_allow_cors_credentials = True
        self.webapp_env_bind_host = "0.0.0.0"
        self.webapp_env_bind_port = 5001
        self.webapp_env_cors_methods = ["*"]
        self.webapp_env_db_dsn = (
            f"postgresql://{self.db_user}:{self.db_password}@db:5432/{self.db_name}"
        )
        self.webapp_env_debug = _debug

    @classmethod
    def from_config_parser(cls, config_parser: configparser.ConfigParser):
        tls_cert_path = config_parser["reverse_proxy"].get("tls_cert_path")
        tls_cert_key_path = config_parser["reverse_proxy"].get("tls_cert_key_path")
        station_blacklist = [
            i.strip()
            for i in config_parser["main"]["observation_station_blacklist"].split(",")
            if i != ""
        ]
        return cls(
            arpa_fvg_auth_token_path=Path(
                config_parser["main"]["arpa_fvg_auth_token_path"]
            ),
            backend_image=config_parser["main"]["backend_image"],
            compose_template=config_parser["main"]["compose_template"],
            db_image_tag=config_parser["main"]["db_image_tag"],
            db_name=config_parser["db"]["name"],
            db_password=config_parser["db"]["password"],
            db_user=config_parser["db"]["user"],
            deployment_files_repo=config_parser["main"]["deployment_files_repo"],
            deployment_files_repo_clone_destination=Path(
                config_parser["main"]["deployment_files_repo_clone_destination"]
            ),
            deployment_root=Path(config_parser["main"]["deployment_root"]),
            discord_notification_urls=[
                i.strip()
                for i in config_parser["main"]["discord_notification_urls"].split(",")
                if i != ""
            ],
            frontend_image=config_parser["main"]["frontend_image"],
            martin_image_tag=config_parser["martin"]["image_tag"],
            martin_config_source=config_parser["martin"]["config_source"],
            observation_station_blacklist=json.dumps(station_blacklist),
            observation_stations_refresher_flow_cron_schedule=(
                config_parser["main"][
                    "observation_stations_refresher_flow_cron_schedule"
                ]
            ),
            observation_measurements_refresher_flow_cron_schedule=(
                config_parser["main"][
                    "observation_measurements_refresher_flow_cron_schedule"
                ]
            ),
            station_variables_refresher_flow_cron_schedule=(
                config_parser["main"]["station_variables_refresher_flow_cron_schedule"]
            ),
            prefect_db_name=config_parser["prefect_db"]["name"],
            prefect_db_password=config_parser["prefect_db"]["password"],
            prefect_db_user=config_parser["prefect_db"]["user"],
            prefect_server_image_tag=config_parser["main"]["prefect_server_image_tag"],
            reverse_proxy_image_tag=config_parser["reverse_proxy"]["image_tag"],
            reverse_proxy_main_domain_name=config_parser["reverse_proxy"][
                "main_domain_name"
            ],
            reverse_proxy_tolgee_domain_name=config_parser["reverse_proxy"][
                "tolgee_domain_name"
            ],
            tls_cert_path=Path(tls_cert_path) if tls_cert_path is not None else None,
            tls_cert_key_path=Path(tls_cert_key_path)
            if tls_cert_key_path is not None
            else None,
            tolgee_app_env_tolgee_authentication_initial_password=config_parser[
                "tolgee_app"
            ]["env_tolgee_authentication_initial_password"],
            tolgee_app_env_tolgee_authentication_jwt_secret=config_parser["tolgee_app"][
                "env_tolgee_authentication_jwt_secret"
            ],
            tolgee_app_env_tolgee_frontend_url=config_parser["tolgee_app"][
                "env_tolgee_frontend_url"
            ],
            tolgee_app_image_tag=config_parser["tolgee_app"]["image_tag"],
            tolgee_db_name=config_parser["tolgee_db"]["name"],
            tolgee_db_password=config_parser["tolgee_db"]["password"],
            tolgee_db_user=config_parser["tolgee_db"]["user"],
            traefik_config_source=config_parser["reverse_proxy"][
                "traefik_config_source"
            ],
            traefik_file_provider_source=config_parser["reverse_proxy"].get(
                "traefik_file_provider_source"
            ),
            traefik_users_file_path=Path(
                config_parser["reverse_proxy"]["traefik_users_file_path"]
            ),
            webapp_env_admin_user_password=config_parser["webapp"][
                "env_admin_user_password"
            ],
            webapp_env_admin_user_username=config_parser["webapp"][
                "env_admin_user_username"
            ],
            webapp_env_cors_origins=[
                i.strip()
                for i in config_parser["webapp"]["env_cors_origins"].split(",")
                if i != ""
            ],
            webapp_env_db_pool_size=int(config_parser["webapp"]["env_db_pool_size"]),
            webapp_env_http_client_timeout_seconds=float(
                config_parser["webapp"].get("env_http_client_timeout_seconds", 30.0)
            ),
            webapp_env_num_uvicorn_worker_processes=config_parser.getint(
                "webapp", "env_num_uvicorn_worker_processes"
            ),
            webapp_env_public_url=config_parser["webapp"]["env_public_url"],
            webapp_env_session_secret_key=config_parser["webapp"][
                "env_session_secret_key"
            ],
            webapp_env_thredds_server_base_url=config_parser["webapp"][
                "env_thredds_server_base_url"
            ],
            webapp_env_uvicorn_log_config_file=Path(
                config_parser["webapp"]["env_uvicorn_log_config_file"]
            ),
            webapp_env_vector_tile_server_base_url=config_parser["webapp"][
                "env_vector_tile_server_base_url"
            ],
        )

    def ensure_paths_exist(self, raise_error: bool = True) -> None:
        paths_to_test = (
            self.deployment_root,
            self.tls_cert_path,
            self.tls_cert_key_path,
        )
        for path in (p for p in paths_to_test if p is not None):
            if not path.exists():
                message = f"Could not find referenced configuration file {path!r}"
                if raise_error:
                    raise RuntimeError(message)
                else:
                    logger.warning(message)


class DeployStepProtocol(Protocol):
    name: str
    config: DeploymentConfiguration

    def handle(self) -> None:
        ...


@dataclasses.dataclass
class _CloneRepo:
    config: DeploymentConfiguration
    name: str = "clone git repository to a temporary directory"

    def handle(self) -> None:
        print("Cloning repo...")
        if self.config.deployment_files_repo_clone_destination.exists():
            shutil.rmtree(self.config.deployment_files_repo_clone_destination)
        subprocess.run(
            shlex.split(
                f"git clone {self.config.deployment_files_repo} "
                f"{self.config.deployment_files_repo_clone_destination}"
            ),
            check=True,
        )


@dataclasses.dataclass
class _CopyRelevantRepoFiles:
    config: DeploymentConfiguration
    name: str = (
        "Copy files relevant to the deployment from temporary git clone "
        "to target location"
    )

    def handle(self) -> None:
        _base = self.config.deployment_files_repo_clone_destination
        to_copy_martin_conf_file_path = _base / self.config.martin_config_source
        to_copy_traefik_conf_file_path = _base / self.config.traefik_config_source
        to_copy_traefik_file_provider_conf_file_path = (
            _base / self.config.traefik_file_provider_source
            if self.config.traefik_file_provider_source is not None
            else None
        )
        deployment_related_file_paths = (
            _base / "deployments/deploy.py",
            _base / self.config.compose_template,
        )
        all_files_to_copy = (
            *deployment_related_file_paths,
            to_copy_martin_conf_file_path,
            to_copy_traefik_conf_file_path,
            to_copy_traefik_file_provider_conf_file_path,
        )
        for to_copy_path in (f for f in all_files_to_copy if f is not None):
            if not to_copy_path.exists():
                raise RuntimeError(
                    f"Could not find expected file in the previously cloned "
                    f"git repo: {to_copy_path!r}"
                )
        for to_copy_path in deployment_related_file_paths:
            shutil.copyfile(
                to_copy_path, self.config.deployment_root / to_copy_path.name
            )
        shutil.copyfile(to_copy_martin_conf_file_path, self.config.martin_conf_path)
        shutil.copyfile(to_copy_traefik_conf_file_path, self.config.traefik_conf_path)
        if to_copy_traefik_file_provider_conf_file_path is not None:
            shutil.copyfile(
                to_copy_traefik_file_provider_conf_file_path,
                self.config.traefik_file_provider_conf_path,
            )


@dataclasses.dataclass
class _RelaunchDeploymentScript:
    config: DeploymentConfiguration
    original_call_args: list[str]
    name: str = "Relaunch the updated deployment script"

    def handle(self) -> None:
        call_args = self.original_call_args[:]
        try:
            call_args.index(_DO_NOT_UPDATE_FLAG_NAME)
        except ValueError:
            # prevent infinite loops by ensuring we set the --no-auto-update flag
            call_args.append(_DO_NOT_UPDATE_FLAG_NAME)
        sys.stdout.flush()
        os.execv(sys.executable, call_args)


@dataclasses.dataclass
class _GenerateComposeFile:
    config: DeploymentConfiguration
    name: str = "generate docker compose file"

    def handle(self) -> None:
        compose_template_path = (
            self.config.deployment_files_repo_clone_destination
            / self.config.compose_template
        )
        compose_template = Template(compose_template_path.read_text())

        render_context = dataclasses.asdict(self.config)
        render_kwargs = {}
        # conf keys that have 'env_' in their name are going to be put as env values
        # inside the container and will be consumed by pydantic. If one of these is
        # a list we dump it as JSON in order to ensure correct handling of
        # parameters that represent collections, for example cors origins, which
        # is a list of strings
        for key, value in render_context.items():
            if "env_" in key and isinstance(value, list):
                render_kwargs[key] = json.dumps(value)

        rendered = compose_template.substitute(render_context, **render_kwargs)
        target_path = Path(self.config.deployment_root / "compose.yaml")
        with target_path.open("w") as fh:
            for line in rendered.splitlines(keepends=True):
                if not line.startswith("#"):
                    fh.write(line)
        compose_template_path.unlink(missing_ok=True)


@dataclasses.dataclass
class _ComposeCommandExecutor:
    config: DeploymentConfiguration
    environment: dict[str, str] | None = None

    def handle(self) -> None:
        raise NotImplementedError

    def _run_compose_command(self, suffix: str) -> subprocess.CompletedProcess:
        compose_file_path = self.config.deployment_root / "compose.yaml"
        if not compose_file_path.exists():
            raise FileNotFoundError()
        docker_compose_command = f"docker compose -f {compose_file_path} {suffix}"
        return subprocess.run(
            shlex.split(docker_compose_command),
            cwd=self.config.deployment_root,
            env=self.environment or os.environ,
            check=True,
        )


class _StartCompose(_ComposeCommandExecutor):
    name: str = "start docker compose"

    def handle(self) -> None:
        print("Restarting the docker compose stack...")
        self._run_compose_command("up --detach --force-recreate")


class _StopCompose(_ComposeCommandExecutor):
    name: str = "stop docker compose"

    def handle(self) -> None:
        print("Stopping docker compose stack...")
        try:
            self._run_compose_command("down")
        except FileNotFoundError:
            logger.info("Failed to stop docker compose stack - compose file not found")
        except subprocess.CalledProcessError as exc:
            if exc.returncode == 14:
                logger.info("docker compose stack was not running, no need to stop")
            else:
                raise


@dataclasses.dataclass
class _PullImages(_ComposeCommandExecutor):
    name: str = "pull new docker images from their respective container registries"

    def handle(self) -> None:
        self._run_compose_command("pull")


@dataclasses.dataclass
class _CompileTranslations:
    config: DeploymentConfiguration
    name: str = "compile static translations"

    def handle(self) -> None:
        print("Compiling translations...")
        subprocess.run(
            shlex.split(
                f"docker exec {self.config.executable_webapp_service_name} poetry run "
                f"arpav-cline translations compile"
            ),
            check=True,
        )


@dataclasses.dataclass
class _RunMigrations:
    config: DeploymentConfiguration
    name: str = "run DB migrations"

    def handle(self) -> None:
        subprocess.run(
            shlex.split(
                f"docker exec {self.config.executable_webapp_service_name} poetry run "
                f"arpav-cline db upgrade"
            ),
            check=True,
        )


@dataclasses.dataclass
class _SendDiscordChannelNotification:
    config: DeploymentConfiguration
    content: str
    name: str = "send a notification to a discord channel"

    def handle(self) -> None:
        for webhook_url in self.config.discord_notification_urls:
            request = urllib.request.Request(webhook_url, method="POST")
            request.add_header("Content-Type", "application/json")

            # the discord server blocks the default user-agent sent by urllib, the
            # one sent by httpx works, so we just use that
            request.add_header("User-Agent", "python-httpx/0.27.0")
            try:
                print(f"Sending notification to {webhook_url!r}...")
                with urllib.request.urlopen(
                    request, data=json.dumps({"content": self.content}).encode("utf-8")
                ) as response:
                    if 200 <= response.status <= 299:
                        print("notification sent")
                    else:
                        print(
                            f"notification response was not successful: {response.status}"
                        )
            except HTTPError:
                print("sending notification failed")


def get_configuration(config_file: Path) -> DeploymentConfiguration:
    config_parser = configparser.ConfigParser()
    config_parser.read(config_file)
    return DeploymentConfiguration.from_config_parser(config_parser)


def perform_deployment(
    *,
    configuration: DeploymentConfiguration,
    auto_update: bool,
    confirmed: bool = False,
):
    deployment_steps = [
        _CloneRepo(config=configuration),
        _CopyRelevantRepoFiles(config=configuration),
    ]
    if auto_update:
        deployment_steps.append(
            _RelaunchDeploymentScript(
                config=configuration, original_call_args=sys.orig_argv
            )
        )
    deployment_steps.extend(
        [
            _StopCompose(config=configuration),
            _GenerateComposeFile(config=configuration),
            _PullImages(config=configuration),
            _StartCompose(config=configuration),
            _RunMigrations(config=configuration),
            _CompileTranslations(config=configuration),
        ]
    )
    this_host = socket.gethostname()
    if len(configuration.discord_notification_urls) > 0:
        deployment_steps.append(
            _SendDiscordChannelNotification(
                config=configuration,
                content=(
                    f"A new deployment of ARPAV-Cline to {this_host!r} has finished"
                ),
            )
        )
    if not confirmed:
        print("Performing a dry-run")
    for step in deployment_steps:
        print(f"Running step: {step.name!r}...")
        if confirmed:
            step.handle()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--config-file",
        default=Path.home() / "arpav-cline/deployment.cfg",
        help="Path to configuration file",
        type=Path,
    )
    parser.add_argument(
        _DO_NOT_UPDATE_FLAG_NAME,
        action="store_true",
        help=(
            "Whether to avoid auto-updating this deployment script with the current "
            "version from the repo. The default is to update this script and then "
            "relaunch, which ensures it runs the most up to date deployer."
        ),
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Turn on debug logging level",
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        help=(
            "Perform the actual deployment. If this is not provided the script runs "
            "in dry-run mode, just showing what steps would be performed"
        ),
    )
    parser.add_argument(
        "-b",
        "--backend-image",
        help=(
            "Full name of the docker image to be used for the backend. "
            "Example: "
            "'ghcr.io/geobeyond/arpav-cline-backend/arpav-cline-backend:v1.0.0'. "
            "Defaults to whatever is specified in the configuration file."
        ),
    )
    parser.add_argument(
        "-f",
        "--frontend-image",
        help=(
            "Full name of the docker image to be used for the frontend. "
            "Example: 'ghcr.io/geobeyond/arpav-cline-frontend/arpav-cline-frontend:v1.0.0'. "
            "Defaults to whatever is specified in the configuration file."
        ),
    )
    parsed_args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if parsed_args.verbose else logging.WARNING)
    config_file = parsed_args.config_file.resolve()
    logger.debug(f"{config_file=}")
    if config_file.exists():
        deployment_config = get_configuration(config_file)
        if (backend_image_name := parsed_args.backend_image) is not None:
            deployment_config.backend_image = backend_image_name
        if (frontend_image_name := parsed_args.frontend_image) is not None:
            deployment_config.frontend_image = frontend_image_name
        deployment_config.ensure_paths_exist(raise_error=parsed_args.confirm)
        logger.debug("Configuration:")
        for k, v in dataclasses.asdict(deployment_config).items():
            logger.debug(f"{k}: {v}")
        try:
            perform_deployment(
                configuration=deployment_config,
                auto_update=not parsed_args.no_auto_update,
                confirmed=parsed_args.confirm,
            )
        except RuntimeError as err:
            raise SystemExit(err) from err
    else:
        raise SystemExit(f"Configuration file {str(config_file)!r} not found")
