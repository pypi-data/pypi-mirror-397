import asyncio
import copy
import getpass
import logging
import os
from pathlib import Path
import socket
from datetime import datetime, timedelta
from time import sleep
from cement import CaughtSignal
import sqlite3
from sqlalchemy import text

# import yaml
from hmd_cli_tools.hmd_cli_tools import get_env_var
from hmd_entity_storage import SqliteEngine
from hmd_graphql_client.hmd_db_engine_client import DbEngineClient
from hmd_lang_librarian_sync.hmd_lang_librarian_sync_client import (
    HmdLangLibrarianSyncClient,
    get_client_schema_root,
)
from hmd_lib_auth.hmd_lib_auth import (
    okta_service_account_token,
    okta_service_account_token_by_secret_name,
)
from hmd_lib_librarian_client.hmd_lib_librarian_client import HmdLibrarianClient
from hmd_schema_loader import DefaultLoader
import requests

from .config.validate_config import load_and_validate_config
from .log import build_dd_sender, get_dd_tags
from .source_handlers import make_source
from .telemetry.metrics import (
    record_queue_size,
    record_sync_cycle_duration,
    record_system_metrics,
    record_db_cleanup_run,
    record_db_cleanup_entities_deleted,
    record_db_cleanup_relationships_deleted,
    record_db_vacuum_run,
)

try:
    from hmd_lib_telemetry import configure_telemetry

    TELEMETRY_AVAILABLE = True
except ImportError:
    TELEMETRY_AVAILABLE = False
    configure_telemetry = None

logger = logging.getLogger(__name__)
send_datadog_event = build_dd_sender(logger)
OKTA_SECRET_NAME = "okta-agent-service"


def get_sleep_time(sleep_time: int = 1) -> int:
    return int(2**sleep_time) if sleep_time < 10 else 10


def execute_sqlite_with_retry(func, max_retries=5, initial_wait=0.1):
    """
    Execute a SQLite operation with retry logic for database locked errors.

    Args:
        func: Callable that performs the SQLite operation
        max_retries: Maximum number of retry attempts (default: 5)
        initial_wait: Initial wait time in seconds, doubles with each retry (default: 0.1)

    Returns:
        The return value from func

    Raises:
        The last exception encountered if all retries are exhausted
    """
    wait_time = initial_wait
    last_exception = None

    for attempt in range(max_retries):
        try:
            return func()
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e).lower():
                last_exception = e
                if attempt < max_retries - 1:
                    logger.warning(
                        f"Database locked, retrying in {wait_time:.2f}s (attempt {attempt + 1}/{max_retries})"
                    )
                    sleep(wait_time)
                    wait_time *= 2  # Exponential backoff
                else:
                    logger.error(
                        f"Database locked after {max_retries} attempts, giving up"
                    )
            else:
                raise
        except Exception as e:
            # For non-lock exceptions, check if the underlying cause is a database lock
            if "database is locked" in str(e).lower():
                last_exception = e
                if attempt < max_retries - 1:
                    logger.warning(
                        f"Database locked, retrying in {wait_time:.2f}s (attempt {attempt + 1}/{max_retries})"
                    )
                    sleep(wait_time)
                    wait_time *= 2
                else:
                    logger.error(
                        f"Database locked after {max_retries} attempts, giving up"
                    )
            else:
                raise

    # If we get here, all retries were exhausted
    raise last_exception


class LibrarianSyncManager:
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
        self, schema_location: Path, db_location: Path
    ) -> HmdLangLibrarianSyncClient:
        loader = DefaultLoader(str(schema_location))
        engine = SqliteEngine(db_location)
        db_client = DbEngineClient(engine, loader)
        return HmdLangLibrarianSyncClient(db_client)

    def __init__(self, instance_config):
        self.hmd_home = Path(os.path.expandvars(get_env_var("HMD_HOME")))
        hmd_repo_home = get_env_var("HMD_REPO_HOME", False)
        if hmd_repo_home:
            self.hmd_repo_home = Path(os.path.expandvars(hmd_repo_home))
        else:
            self.hmd_repo_home = None
        self.schema_uri = None
        schema_uri = get_env_var("SCHEMA_URI", False)
        if schema_uri:
            self.schema_uri = Path(schema_uri)
        schema_location = self.__resolve_schema_location()
        db_location = self.__ensure_db()
        librarian_sync_client = self.__build_client(schema_location, db_location)
        self.librarian_sync_client = librarian_sync_client
        self.instance_config = instance_config

        if os.path.isfile(self.instance_config):
            self.abs_config_path = Path((Path.cwd() / self.instance_config).absolute())
            config = load_and_validate_config(self.abs_config_path, validate=False)
        else:
            config = load_and_validate_config(self.instance_config, validate=False)

        self.manifest_nid = os.environ.get("HMD_ENTITY_NID")
        for librarian_name, librarian in config["librarians"].items():
            if config["librarians"][librarian_name].get("url") == "default":
                url = os.environ.get(f"HMD_{librarian_name.upper()}_LIBRARIAN_URL")
                if url:
                    config["librarians"][librarian_name]["url"] = url
                else:
                    raise Exception(
                        f"Librarian {librarian_name} is not configured with an url endpoint."
                    )
            if config["librarians"][librarian_name].get("api_key"):
                if config["librarians"][librarian_name]["api_key"] == "default":
                    key = os.environ.get(f"HMD_{librarian_name.upper()}_LIBRARIAN_KEY")
                    config["librarians"][librarian_name]["api_key"] = (
                        key if key != "default" else None
                    )
            else:
                auth_token = None
                sleep_time = 0
                if config["librarians"][librarian_name].get("cert_file"):
                    continue
                while auth_token is None:
                    try:
                        if self.manifest_nid:
                            auth_token = okta_service_account_token_by_secret_name(
                                OKTA_SECRET_NAME
                            )
                        else:
                            auth_token = okta_service_account_token(
                                os.environ["HMD_AGENT_CLIENT_ID"],
                                os.environ["HMD_AGENT_CLIENT_SECRET"],
                                okta_host_url=os.environ["HMD_SERVICES_ISSUER"],
                            )
                        config["librarians"][librarian_name]["auth_token"] = auth_token
                    except requests.exceptions.ConnectionError as e:
                        logger.error(
                            f"Connection error while retrieving auth token for {librarian_name}: {e}"
                        )
                        sleep_time = get_sleep_time(sleep_time)
                        sleep(sleep_time)  # Wait before retrying
                    except requests.exceptions.Timeout as e:
                        logger.error(
                            f"Timeout error while retrieving auth token for {librarian_name}: {e}"
                        )
                        sleep_time = get_sleep_time(sleep_time)
                        sleep(sleep_time)  # Wait before retrying
                    except Exception as e:
                        raise Exception(
                            f"Error retrieving auth token for {librarian_name}: {e}"
                        )

        self._config = config
        self.timestamp_reverse: bool = config.get("timestamp_sort", "asc") == "desc"

        self.archive_root = None
        if "archive_root" in self._config:
            self.archive_root = Path(os.path.expandvars(self._config["archive_root"]))

        def make_librarian_client(config):
            username = getpass.getuser()
            headers = {
                "X-NeuronSphere-User-Email": username,
                "X-NeuronSphere-Host": os.environ.get(
                    "HMD_HOSTNAME", socket.gethostname()
                ),
            }
            cert_key = config.get("cert_key")
            client_cert = config.get("cert_file")
            client_certs = None
            if cert_key and client_cert:
                cert_key = os.path.expandvars(cert_key)
                client_cert = os.path.expandvars(client_cert)
                if os.path.isfile(cert_key) and os.path.isfile(client_cert):
                    client_certs = (client_cert, cert_key)
                    headers = {
                        "X-NeuronSphere-Host": os.environ.get(
                            "HMD_HOSTNAME", socket.gethostname()
                        ),
                    }
                else:
                    raise FileNotFoundError(
                        f"Client cert or key file not found: {client_cert}, {cert_key}"
                    )
            return HmdLibrarianClient(
                base_url=config.get("url"),
                api_key=config.get("api_key"),
                auth_token=config.get("auth_token"),
                extra_headers=headers,
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
                return librarian_clients[source_config.get("target")]
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
                timestamp_reverse=self.timestamp_reverse,
            ),
            self._config["sources"].items(),
        )

        self.sources = list(filter(lambda x: x.is_enabled, all_sources))
        self.source_map = {s.name: s for s in self.sources}

        # Run VACUUM on startup to reclaim space from previous cleanups
        self._vacuum_database_on_startup(db_location)

        # Configure telemetry if requested
        self._configure_telemetry_from_config()

    def _vacuum_database_on_startup(self, db_location: Path):
        """
        Run VACUUM on the database at startup to reclaim space from previous cleanups.

        This runs during initialization before any sync operations start, so blocking is acceptable.
        """
        db_cleanup_config = self._config.get("db_cleanup")
        if not db_cleanup_config:
            logger.debug("Database cleanup not configured, skipping VACUUM on startup")
            return

        try:
            import time

            db_size_before_bytes = db_location.stat().st_size
            db_size_before = db_size_before_bytes / (1024 * 1024)
            logger.info(
                f"Running VACUUM on startup to reclaim database space (current size: {db_size_before:.2f} MB)..."
            )

            # Get the SQLite engine from the librarian_sync_client
            engine = self.librarian_sync_client._base_client.db_engine._engine

            vacuum_start_time = time.time()

            def run_vacuum():
                with engine.connect() as conn:
                    conn.execute(text("VACUUM"))
                    conn.commit()

            # Execute VACUUM with retry logic for database locks
            execute_sqlite_with_retry(run_vacuum, max_retries=10, initial_wait=1.0)

            vacuum_duration = time.time() - vacuum_start_time

            db_size_after_bytes = db_location.stat().st_size
            db_size_after = db_size_after_bytes / (1024 * 1024)
            space_reclaimed_bytes = db_size_before_bytes - db_size_after_bytes
            space_reclaimed = db_size_before - db_size_after

            if space_reclaimed > 0:
                logger.info(
                    f"VACUUM completed: database size reduced from {db_size_before:.2f} MB to {db_size_after:.2f} MB (reclaimed {space_reclaimed:.2f} MB)"
                )
            else:
                logger.info(
                    f"VACUUM completed: no space reclaimed (database size: {db_size_after:.2f} MB)"
                )

            # Record metrics
            record_db_vacuum_run(vacuum_duration, space_reclaimed_bytes)

        except Exception as e:
            logger.error(f"Error during VACUUM on startup: {e}", exc_info=True)

    def _configure_telemetry_from_config(self):
        """
        Configure telemetry based on the librarian-sync configuration.

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
                            service_name=f"{service_name_override}-manager",
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
                    f"Telemetry librarian '{telemetry_librarian}' not found in librarians configuration"
                )

    def _cleanup_old_file_uploads(self, db_location: Path):
        """
        Check database size and delete old FileUpload entities if threshold is exceeded.

        This method checks if the database exceeds the configured size threshold,
        and if so, performs hard deletes of FileUpload entities and their relationships
        older than the configured retention period using raw SQL DELETE statements.

        If the database exceeds the maximum threshold, VACUUM is run immediately to reclaim space.
        """
        db_cleanup_config = self._config.get("db_cleanup")
        if not db_cleanup_config:
            logger.debug("Database cleanup not configured, skipping")
            return

        size_threshold_mb = db_cleanup_config.get("size_threshold_mb")
        size_max_threshold_mb = db_cleanup_config.get("size_max_threshold_mb")
        retention_days = db_cleanup_config.get("retention_days")

        if size_threshold_mb is None or retention_days is None:
            logger.warning("Database cleanup configuration incomplete, skipping")
            return

        # Check database size
        db_size_bytes = db_location.stat().st_size
        db_size_mb = db_size_bytes / (1024 * 1024)

        logger.info(
            f"Database size: {db_size_mb:.2f} MB (threshold: {size_threshold_mb} MB)"
        )

        if db_size_mb <= size_threshold_mb:
            logger.debug("Database size below threshold, skipping cleanup")
            return

        logger.info(
            f"Database size exceeds threshold, performing cleanup of FileUpload entities older than {retention_days} days"
        )

        # Check if we need to run VACUUM immediately
        needs_immediate_vacuum = False
        if size_max_threshold_mb and db_size_mb > size_max_threshold_mb:
            logger.warning(
                f"Database size {db_size_mb:.2f} MB exceeds maximum threshold {size_max_threshold_mb} MB - VACUUM will run after cleanup to reclaim space immediately"
            )
            needs_immediate_vacuum = True

        # Calculate cutoff datetime (retention_days ago)
        cutoff_datetime = (datetime.now() - timedelta(days=retention_days)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        try:
            import time

            # Get the SQLite engine from the librarian_sync_client
            engine = self.librarian_sync_client._base_client.db_engine._engine

            # Variables to track deletion results
            old_upload_ids = None
            relationships_deleted = 0
            entities_deleted = 0

            def run_cleanup():
                nonlocal old_upload_ids, relationships_deleted, entities_deleted
                # Use raw SQL to perform hard deletes
                with engine.connect() as conn:
                    # First, get the IDs of old FileUpload entities to delete based on updated_at column
                    query_old_uploads = text(
                        f"""
                        SELECT id FROM entity
                        WHERE name = 'hmd_lang_librarian_sync.file_upload'
                        AND updated_at < '{cutoff_datetime}'
                        AND is_deleted = 0
                    """
                    )
                    result = conn.execute(query_old_uploads)
                    old_upload_ids = [row[0] for row in result.fetchall()]

                    if not old_upload_ids:
                        return

                    # Delete FileToUpload relationships that reference these FileUpload entities
                    # (where FileUpload is the 'to' side of the relationship)
                    ids_placeholder = ",".join([f"'{id}'" for id in old_upload_ids])
                    delete_relationships_query = text(
                        f"""
                        DELETE FROM relationship
                        WHERE name = 'hmd_lang_librarian_sync.file_to_upload'
                        AND to_id IN ({ids_placeholder})
                    """
                    )
                    result = conn.execute(delete_relationships_query)
                    relationships_deleted = result.rowcount

                    # Delete the FileUpload entities themselves
                    delete_entities_query = text(
                        f"""
                        DELETE FROM entity
                        WHERE name = 'hmd_lang_librarian_sync.file_upload'
                        AND id IN ({ids_placeholder})
                    """
                    )
                    result = conn.execute(delete_entities_query)
                    entities_deleted = result.rowcount

                    # Commit the transaction
                    conn.commit()

            # Execute cleanup with retry logic for database locks
            execute_sqlite_with_retry(run_cleanup, max_retries=5, initial_wait=0.5)

            if not old_upload_ids:
                logger.info("No old FileUpload entities found to delete")
                return

            logger.info(f"Found {len(old_upload_ids)} FileUpload entities to delete")
            logger.info(f"Deleted {relationships_deleted} FileToUpload relationships")
            logger.info(f"Deleted {entities_deleted} FileUpload entities")
            logger.info(
                f"Successfully deleted {entities_deleted} FileUpload entities and {relationships_deleted} relationships"
            )

            # Record cleanup metrics
            record_db_cleanup_run()
            record_db_cleanup_entities_deleted(entities_deleted)
            record_db_cleanup_relationships_deleted(relationships_deleted)

            # If database size exceeded max threshold, run VACUUM immediately
            if needs_immediate_vacuum:
                logger.warning(
                    "Running VACUUM immediately due to maximum threshold exceeded (this will block uploads temporarily)..."
                )
                db_size_before_bytes = db_location.stat().st_size
                vacuum_start_time = time.time()

                def run_emergency_vacuum():
                    with engine.connect() as conn:
                        conn.execute(text("VACUUM"))
                        conn.commit()

                # Execute emergency VACUUM with retry logic
                execute_sqlite_with_retry(
                    run_emergency_vacuum, max_retries=10, initial_wait=1.0
                )

                vacuum_duration = time.time() - vacuum_start_time

                # Check new database size after VACUUM
                db_size_after_bytes = db_location.stat().st_size
                new_db_size_mb = db_size_after_bytes / (1024 * 1024)
                space_reclaimed = db_size_mb - new_db_size_mb
                space_reclaimed_bytes = db_size_before_bytes - db_size_after_bytes
                logger.info(
                    f"Emergency VACUUM completed: database size reduced from {db_size_mb:.2f} MB to {new_db_size_mb:.2f} MB (reclaimed {space_reclaimed:.2f} MB)"
                )

                # Record VACUUM metrics
                record_db_vacuum_run(vacuum_duration, space_reclaimed_bytes)

        except Exception as e:
            logger.error(f"Error during database cleanup: {e}", exc_info=True)

    def get_queued_files(self):
        files = []
        for source in self.sources:
            files.extend(source.get_queued_files())
        # Sort based on modified time, default is older files first
        files = sorted(
            files,
            key=lambda f: f.modified,
            reverse=self.timestamp_reverse,
        )
        # Sort based on priority
        files = sorted(files, key=lambda f: f.upload_priority, reverse=True)
        return files

    def get_queued_file(self):
        files = self.get_queued_files()
        logger.info(len(files))
        while len(files) > 0:
            yield files[0]
            files = self.get_queued_files()
            logger.info(f"Found {len(files)} files...")
        logger.info("Return")
        return

    async def _sync(self, watch=True):
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
        sanitized_config = copy.copy(self._config)
        for lib_name, lib_config in sanitized_config["librarians"].items():
            if "auth_token" in lib_config:
                lib_config.pop("auth_token")
        logger.debug(f"Config: {sanitized_config}")
        logger.info("BEGIN sync")
        db_location = self.__ensure_db()
        while True:
            cycle_start_time = asyncio.get_event_loop().time()
            stop_requested = False
            is_complete = False
            attempt_max_reached = False
            if stop_requested:
                logger.info(f"{self.name}: Stop requested, skipping sync")
                break
            files = self.get_queued_files()
            is_complete = len(files) == 0

            # Record queue size and system metrics
            record_queue_size(len(files))
            record_system_metrics(db_location)

            gen = self.get_queued_file()
            for next_file in gen:
                if stop_requested:
                    logger.info(f"{self.name}: Stop requested, skipping sync")
                    break
                if next_file is None:
                    is_complete = True
                    break
                logger.info(f"Syncing queued file: {next_file.path}")
                source = self.source_map[next_file.source_name]
                source.attempts = 0
                try:
                    if not source.is_complete():
                        source.sync(next_file)
                except CaughtSignal as cs:
                    logger.error("Caught Signal", exc_info=cs)
                    stop_requested = True
                    break
                except BaseException as e:
                    logger.error("Sync failed", exc_info=e)
                    send_datadog_event(
                        event_type="error",
                        data=(
                            f"Librarian Sync Watcher failed during {source.name} sync"
                            if watch
                            else f"Librarian Sync Manager failed during {source.name} sync"
                        ),
                        ex=str(e),
                        tags=get_dd_tags(),
                    )
                    break
                source_is_complete = source.is_complete()
                is_complete = is_complete and source_is_complete
                if not source_is_complete:
                    attempt_max_reached = (
                        attempt_max_reached or source.attempt_max_reached()
                    )
                if source.type == "manifest":
                    query = {
                        "and": [
                            {
                                "attribute": "source_name",
                                "operator": "=",
                                "value": source.name,
                            }
                        ]
                    }
                    all_files = (
                        self.librarian_sync_client.search_file_hmd_lang_librarian_sync(
                            query
                        )
                    )
                    files_not_synced = [
                        file
                        for file in all_files
                        if file.librarians_synced[source.librarian] != file.modified
                        and file.schedule_upload != 1
                    ]
                    if len(files_not_synced) == 0 and source.type == "manifest":
                        for file in all_files:
                            if Path(file.path).exists():
                                source.handle_file_delete(file)
            if stop_requested:
                break

            # Record sync cycle duration
            cycle_duration = asyncio.get_event_loop().time() - cycle_start_time
            record_sync_cycle_duration(cycle_duration)

            # Perform database cleanup check after each sync cycle
            self._cleanup_old_file_uploads(db_location)

            if watch:
                await asyncio.sleep(5)

            elif is_complete:
                break
            elif attempt_max_reached:
                send_datadog_event(
                    event_type="error",
                    data=(
                        "Librarian Sync Watcher failure"
                        if watch
                        else "Librarian Sync Manager failure"
                    ),
                    ex="Max attempts reached",
                    tags=get_dd_tags(),
                )
        logger.info("END sync")

    def sync(self):
        try:
            asyncio.run(self._sync(False))
        except BaseException as e:
            logger.error("Manager Sync failed", exc_info=e)
            raise e

    def start(self):
        try:
            logger.info("Starting watcher")
            send_datadog_event(
                event_type="info",
                data="Librarian sync watcher started",
                tags=get_dd_tags(),
            )
            asyncio.run(self._sync())
        except BaseException as e:
            logger.error("Watcher failed", exc_info=e)
            raise e

    def stop(self):
        logger.info("Stopping Manager")
        for source in self.sources:
            source.stop()
        logger.info("all tasks stopped")
