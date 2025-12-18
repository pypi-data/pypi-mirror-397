import asyncio
import getpass
import logging
import os
from pathlib import Path
import socket
import time

from hmd_cli_tools.hmd_cli_tools import get_env_var
from hmd_entity_storage import SqliteEngine
from hmd_graphql_client.hmd_db_engine_client import DbEngineClient
from hmd_lang_librarian_sync.hmd_lang_librarian_sync_client import (
    HmdLangLibrarianSyncClient,
    get_client_schema_root,
)
from hmd_lib_librarian_client.hmd_lib_librarian_client import HmdLibrarianClient
from hmd_lib_auth.hmd_lib_auth import okta_service_account_token_by_secret_name
from hmd_schema_loader import DefaultLoader

from .config.validate_config import load_and_validate_config
from .log import build_dd_sender, get_dd_tags
from .source_handlers import make_source

logger = logging.getLogger(__name__)
send_datadog_event = build_dd_sender(logger)
OKTA_SECRET_NAME = "okta-agent-service"

# Import telemetry configuration if available
TELEMETRY_AVAILABLE = False
try:
    from hmd_lib_telemetry.hmd_lib_telemetry import configure_telemetry
    from .telemetry.metrics import record_sync_cycle_duration, record_system_metrics

    TELEMETRY_AVAILABLE = True
except ImportError:
    logger.debug("hmd-lib-telemetry not available, telemetry will be disabled")


class LibrarianSyncWatcher:
    def __resolve_schema_location(self) -> Path:
        schema_location = Path(get_client_schema_root())
        if not schema_location.exists():
            schema_location = self.hmd_home / "language_packs"
        if not schema_location.exists():
            schema_location = (
                self.hmd_home / "client" / "vocabs" / "hmd-lang-librarian-sync"
            )
        if not schema_location.exists() and self.hmd_repo_home:
            schema_location = (
                self.hmd_repo_home / "hmd-lang-librarian-sync" / "src" / "schemas"
            )
        if not schema_location.exists() and self.schema_uri:
            schema_location = self.schema_uri
        if schema_location and schema_location.exists():
            return schema_location
        raise FileNotFoundError("Unable to resolve schema location")

    def __ensure_db(self) -> Path:
        db_location = self.hmd_home / "sqlite" / "data" / "librarian-sync.db"
        db_location.parent.mkdir(parents=True, exist_ok=True)
        return db_location

    def __build_client(
        self, schema_location, db_location
    ) -> HmdLangLibrarianSyncClient:
        loader = DefaultLoader(base=os.path.expandvars(schema_location))
        engine = SqliteEngine(os.path.expandvars(db_location))
        db_client = DbEngineClient(engine, loader)
        return HmdLangLibrarianSyncClient(db_client)

    def _configure_telemetry_from_config(self):
        """Configure telemetry based on the librarian-sync configuration.

        This method checks if there's a telemetry_librarian specified in the config
        and configures OpenTelemetry to send metrics/traces/logs to that librarian.
        """
        if not TELEMETRY_AVAILABLE:
            logger.debug(
                "hmd-lib-telemetry not available, skipping telemetry configuration"
            )
            return

        # Check for telemetry configuration
        telemetry_config = self._config.get("telemetry", {})
        telemetry_librarian = telemetry_config.get("librarian")
        service_name_override = telemetry_config.get("service_name")

        # Also check for HMD_OTEL_TELEMETRY_LIBRARIAN environment variable
        if not telemetry_librarian:
            telemetry_librarian = os.environ.get("HMD_OTEL_TELEMETRY_LIBRARIAN")

        if not service_name_override:
            service_name_override = os.environ.get("HMD_OTEL_SERVICE_NAME")

        if telemetry_librarian:
            librarian_config = self._config["librarians"].get(telemetry_librarian)
            if librarian_config:
                base_url = librarian_config.get("url")
                # Append /apiop/telemetry to the librarian URL for OTEL endpoint
                if base_url:
                    # Remove trailing slash if present
                    base_url = base_url.rstrip("/")
                    otel_endpoint = f"{base_url}/apiop/telemetry"
                    logger.info(
                        f"Configuring telemetry to send to librarian: {telemetry_librarian} at {otel_endpoint}"
                    )

                    # Extract authentication from librarian config
                    auth_token = librarian_config.get("auth_token")
                    client_certs = None
                    cert_file = librarian_config.get("cert_file")
                    cert_key = librarian_config.get("cert_key")
                    if cert_file and cert_key:
                        cert_file = os.path.expandvars(cert_file)
                        cert_key = os.path.expandvars(cert_key)
                        client_certs = (cert_file, cert_key)

                    try:
                        configure_telemetry(
                            otel_endpoint=otel_endpoint,
                            service_name=f"{service_name_override}-watcher"
                            if service_name_override
                            else None,
                            auth_token=auth_token,
                            client_certs=client_certs,
                        )
                        logger.info("Telemetry configured successfully")
                    except Exception as e:
                        logger.error(
                            f"Failed to configure telemetry: {e}", exc_info=True
                        )
                else:
                    logger.warning(
                        f"Telemetry librarian '{telemetry_librarian}' has no URL configured"
                    )
            else:
                logger.warning(
                    f"Telemetry librarian '{telemetry_librarian}' not found in configuration"
                )

    def __init__(self, instance_config):
        self.hmd_home = Path(os.path.expandvars(get_env_var("HMD_HOME")))
        hmd_repo_home = get_env_var("HMD_REPO_HOME", False)
        if hmd_repo_home:
            self.hmd_repo_home = Path(os.path.expandvars(hmd_repo_home))
        else:
            self.hmd_repo_home = None
        os.environ["HMD_INSTANCE_NAME"] = os.environ.get("HMD_INSTANCE_NAME", "agent")
        self.schema_uri = None
        schema_uri = get_env_var("SCHEMA_URI", False)
        if schema_uri:
            self.schema_uri = Path(schema_uri)
        schema_location = self.__resolve_schema_location()
        db_location = self.__ensure_db()
        self.db_location = db_location  # Store for metrics
        librarian_sync_client = self.__build_client(schema_location, db_location)
        self.instance_config = instance_config

        if os.path.isfile(self.instance_config):
            self.abs_config_path = Path((Path.cwd() / self.instance_config).absolute())
            config = load_and_validate_config(self.abs_config_path, validate=False)
        else:
            config = load_and_validate_config(self.instance_config, validate=False)

        self.manifest_nid = os.environ.get("HMD_ENTITY_NID")
        for librarian in config["librarians"]:
            if config["librarians"][librarian].get("url") == "default":
                url = os.environ.get(f"HMD_{librarian.upper()}_LIBRARIAN_URL")
                if url:
                    config["librarians"][librarian]["url"] = url
                else:
                    raise Exception(
                        f"Librarian {librarian} is not configured with an url endpoint."
                    )
            if config["librarians"][librarian].get("api_key"):
                key = os.environ.get(f"HMD_{librarian.upper()}_LIBRARIAN_KEY")
                config["librarians"][librarian]["api_key"] = (
                    key if key != "default" else None
                )
            else:
                if self.manifest_nid:
                    try:
                        auth_token = okta_service_account_token_by_secret_name(
                            OKTA_SECRET_NAME
                        )
                        config["librarians"][librarian]["auth_token"] = auth_token
                    except Exception as e:
                        raise Exception(
                            f"Error retrieving auth token for {librarian}: {e}"
                        )

        self._config = config

        # Configure telemetry from config
        self._configure_telemetry_from_config()

        def make_librarian_client(config):
            username = getpass.getuser()
            cert_key = config.get("cert_key")
            client_cert = config.get("cert_file")
            client_certs = None
            if cert_key and client_cert:
                cert_key = os.path.expandvars(cert_key)
                client_cert = os.path.expandvars(client_cert)
                if os.path.isfile(cert_key) and os.path.isfile(client_cert):
                    client_certs = (client_cert, cert_key)
                else:
                    raise FileNotFoundError(
                        f"Client cert or key file not found: {client_cert}, {cert_key}"
                    )
            return HmdLibrarianClient(
                base_url=config.get("url"),
                api_key=config.get("api_key"),
                auth_token=config.get("auth_token"),
                extra_headers={
                    "X-NeuronSphere-User-Email": username,
                    "X-NeuronSphere-Host": os.environ.get(
                        "HMD_HOSTNAME", socket.gethostname()
                    ),
                },
                client_certs=client_certs,
            )

        librarian_clients = dict(
            map(
                lambda kv: (kv[0], make_librarian_client(kv[1])),
                self._config.get("librarians", {}).items(),
            )
        )

        def get_librarian_client(source_config):
            """Get the appropriate librarian client based on source type and configuration."""
            if source_config.get("type") == "librarian-sync":
                # For librarian-sync sources, use the target librarian
                return librarian_clients[source_config.get("source")]
            # For other sources, use the configured librarian
            return librarian_clients[source_config["librarian"]]

        all_sources = map(
            lambda kv: make_source(
                name=kv[0],
                source=kv[1],
                librarian_sync_client=librarian_sync_client,
                librarian_client=get_librarian_client(kv[1]),
                hmd_home=self.hmd_home,
                hmd_repo_home=self.hmd_repo_home,
            ),
            self._config["sources"].items(),
        )

        self.sources = list(filter(lambda x: x.is_enabled, all_sources))
        self._watcher_tasks = []

    async def watch(self):
        tasks = list(
            map(lambda source: asyncio.create_task(source.start()), self.sources)
        )

        self._watcher_tasks = tasks
        await asyncio.gather(*self._watcher_tasks)

    def sync(self):
        logger.info("Validating config...")
        if os.path.isfile(self.instance_config):
            self.abs_config_path = Path((Path.cwd() / self.instance_config).absolute())
            is_valid, details = load_and_validate_config(
                self.abs_config_path, validate=True
            )
        else:
            is_valid, details = load_and_validate_config(
                self.instance_config, validate=True
            )
        if not is_valid:
            raise details
        logger.info("Config validated")
        logger.debug(f"Config: {self._config}")
        send_datadog_event(
            event_type="success",
            data="Librarian sync watcher configured successfully",
            tags=get_dd_tags(),
        )
        try:
            logger.info("Running sync")
            sync_start_time = time.time()

            # Record system metrics before sync
            if TELEMETRY_AVAILABLE:
                record_system_metrics(self.db_location)

            for source in self.sources:
                source.sync()

            # Record sync cycle duration
            if TELEMETRY_AVAILABLE:
                sync_duration = time.time() - sync_start_time
                record_sync_cycle_duration(sync_duration)
                record_system_metrics(self.db_location)

        except BaseException as e:
            logger.error("Watcher failed", exc_info=e)
            send_datadog_event(
                event_type="error",
                data=f"Librarian Sync Watcher failed during sync",
                ex=str(e),
                tags=get_dd_tags(),
            )
            raise e

    def start(self):
        try:
            logger.info("Starting watcher")
            asyncio.run(self.watch())
        except BaseException as e:
            logger.error("Watcher failed", exc_info=e)
            send_datadog_event(
                event_type="error",
                data="Librarian sync watcher failed to sync",
                ex=str(e),
                tags=get_dd_tags(),
            )
            raise e

    def stop(self):
        for task in self._watcher_tasks:
            task.cancel()
        logger.info("all tasks stopped")
        send_datadog_event(
            event_type="info", data="Librarian sync watcher stopped", tags=get_dd_tags()
        )
