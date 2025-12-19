import os
import psutil
from pathlib import Path
from hmd_lib_telemetry.hmd_lib_telemetry import HmdMetric

# Metric name constants
PUT_FILE_SUCCESS = "put_file_success"
PUT_FILE_FAILURE = "put_file_failure"
PUT_FILE_RETRY = "put_file_retry"
PUT_FILE_MODIFIED_DURING_UPLOAD = "put_file_modified_during_upload"
PUT_FILE_DURATION = "put_file_duration"
UPLOAD_PART_COMPLETE = "upload_part_complete"
UPLOAD_BYTES_TRANSFERRED = "upload_bytes_transferred"
FILE_SIZE_UPLOADED = "file_size_uploaded"
QUEUE_SIZE = "queue_size"
SYNC_CYCLE_DURATION = "sync_cycle_duration"
DB_SIZE_BYTES = "db_size_bytes"
MEMORY_USAGE_BYTES = "memory_usage_bytes"
CPU_USAGE_PERCENT = "cpu_usage_percent"
DB_CLEANUP_RUNS = "db_cleanup_runs"
DB_CLEANUP_ENTITIES_DELETED = "db_cleanup_entities_deleted"
DB_CLEANUP_RELATIONSHIPS_DELETED = "db_cleanup_relationships_deleted"
DB_VACUUM_RUNS = "db_vacuum_runs"
DB_VACUUM_SPACE_RECLAIMED_BYTES = "db_vacuum_space_reclaimed_bytes"
DB_VACUUM_DURATION = "db_vacuum_duration"

# Initialize metric meters
sync_manager_meter = HmdMetric("librarian_sync_manager")

# Counters for file operations
put_file_success_counter = sync_manager_meter.counter(
    PUT_FILE_SUCCESS,
    unit="1",
    description="Count of successful put_file operations",
)

put_file_failure_counter = sync_manager_meter.counter(
    PUT_FILE_FAILURE,
    unit="1",
    description="Count of failed put_file operations",
)

put_file_retry_counter = sync_manager_meter.counter(
    PUT_FILE_RETRY,
    unit="1",
    description="Count of put_file retry attempts",
)

put_file_modified_counter = sync_manager_meter.counter(
    PUT_FILE_MODIFIED_DURING_UPLOAD,
    unit="1",
    description="Count of files modified during upload",
)

# Counters for upload progress
upload_part_counter = sync_manager_meter.counter(
    UPLOAD_PART_COMPLETE,
    unit="1",
    description="Count of upload parts completed",
)

upload_bytes_counter = sync_manager_meter.counter(
    UPLOAD_BYTES_TRANSFERRED,
    unit="By",
    description="Total bytes transferred to librarian",
)

file_size_counter = sync_manager_meter.counter(
    FILE_SIZE_UPLOADED,
    unit="By",
    description="Total size of files successfully uploaded",
)

# Histograms for timing
put_file_duration_hist = sync_manager_meter.histogram(
    PUT_FILE_DURATION,
    unit="s",
    description="Time taken to complete put_file operation",
)

sync_cycle_duration_hist = sync_manager_meter.histogram(
    SYNC_CYCLE_DURATION,
    unit="s",
    description="Time taken to complete a sync cycle",
)

# Gauges for system metrics
queue_size_gauge = sync_manager_meter.up_down_counter(
    QUEUE_SIZE,
    unit="1",
    description="Number of files queued for upload",
)

db_size_gauge = sync_manager_meter.up_down_counter(
    DB_SIZE_BYTES,
    unit="By",
    description="Size of SQLite database in bytes",
)

memory_usage_gauge = sync_manager_meter.up_down_counter(
    MEMORY_USAGE_BYTES,
    unit="By",
    description="Memory usage of the application in bytes",
)

cpu_usage_gauge = sync_manager_meter.up_down_counter(
    CPU_USAGE_PERCENT,
    unit="%",
    description="CPU usage percentage of the application",
)

# Counters for database cleanup operations
db_cleanup_runs_counter = sync_manager_meter.counter(
    DB_CLEANUP_RUNS,
    unit="1",
    description="Count of database cleanup operations performed",
)

db_cleanup_entities_deleted_counter = sync_manager_meter.counter(
    DB_CLEANUP_ENTITIES_DELETED,
    unit="1",
    description="Total number of FileUpload entities deleted during cleanup",
)

db_cleanup_relationships_deleted_counter = sync_manager_meter.counter(
    DB_CLEANUP_RELATIONSHIPS_DELETED,
    unit="1",
    description="Total number of FileToUpload relationships deleted during cleanup",
)

db_vacuum_runs_counter = sync_manager_meter.counter(
    DB_VACUUM_RUNS,
    unit="1",
    description="Count of VACUUM operations performed",
)

db_vacuum_space_reclaimed_counter = sync_manager_meter.counter(
    DB_VACUUM_SPACE_RECLAIMED_BYTES,
    unit="By",
    description="Total space reclaimed by VACUUM operations in bytes",
)

db_vacuum_duration_hist = sync_manager_meter.histogram(
    DB_VACUUM_DURATION,
    unit="s",
    description="Time taken to complete VACUUM operation",
)


# Metric recording functions
def record_put_file_success():
    """Record a successful put_file operation."""
    try:
        put_file_success_counter.add(1)
    except Exception:
        pass


def record_put_file_failure():
    """Record a failed put_file operation."""
    try:
        put_file_failure_counter.add(1)
    except Exception:
        pass


def record_put_file_retry():
    """Record a put_file retry attempt."""
    try:
        put_file_retry_counter.add(1)
    except Exception:
        pass


def record_put_file_modified_during_upload():
    """Record a file being modified during upload."""
    try:
        put_file_modified_counter.add(1)
    except Exception:
        pass


def record_put_file_duration(duration_seconds: float):
    """
    Record the duration of a put_file operation.

    Args:
        duration_seconds: Duration in seconds
    """
    try:
        put_file_duration_hist.record(duration_seconds)
    except Exception:
        pass


def record_upload_part_complete(count: int = 1):
    """
    Record completion of upload parts.

    Args:
        count: Number of parts completed (default: 1)
    """
    try:
        upload_part_counter.add(count)
    except Exception:
        pass


def record_upload_bytes_transferred(bytes_count: int):
    """
    Record bytes transferred during upload.

    Args:
        bytes_count: Number of bytes transferred
    """
    try:
        upload_bytes_counter.add(bytes_count)
    except Exception:
        pass


def record_file_size_uploaded(file_size_bytes: int):
    """
    Record the size of a successfully uploaded file.

    Args:
        file_size_bytes: Size of the file in bytes
    """
    try:
        file_size_counter.add(file_size_bytes)
    except Exception:
        pass


def record_sync_cycle_duration(duration_seconds: float):
    """
    Record the duration of a complete sync cycle.

    Args:
        duration_seconds: Duration in seconds
    """
    try:
        sync_cycle_duration_hist.record(duration_seconds)
    except Exception:
        pass


def record_queue_size(queue_size: int):
    """
    Record the current queue size.

    Args:
        queue_size: Number of files in the queue
    """
    try:
        queue_size_gauge.add(queue_size)
    except Exception:
        pass


def record_db_size(db_path: Path):
    """
    Record the current size of the SQLite database.

    Args:
        db_path: Path to the SQLite database file
    """
    try:
        if db_path.exists():
            size_bytes = db_path.stat().st_size
            db_size_gauge.add(size_bytes)
    except Exception:
        pass


def record_memory_usage():
    """Record the current memory usage of the application."""
    try:
        process = psutil.Process(os.getpid())
        memory_bytes = process.memory_info().rss
        memory_usage_gauge.add(memory_bytes)
    except Exception:
        pass


def record_cpu_usage():
    """Record the current CPU usage percentage of the application."""
    try:
        process = psutil.Process(os.getpid())
        cpu_percent = process.cpu_percent(interval=0.1)
        cpu_usage_gauge.add(cpu_percent)
    except Exception:
        pass


def record_system_metrics(db_path: Path = None):
    """
    Record all system metrics (memory, CPU, database size).

    Args:
        db_path: Path to the SQLite database file (optional)
    """
    record_memory_usage()
    record_cpu_usage()
    if db_path:
        record_db_size(db_path)


def record_db_cleanup_run():
    """Record that a database cleanup operation was performed."""
    try:
        db_cleanup_runs_counter.add(1)
    except Exception:
        pass


def record_db_cleanup_entities_deleted(count: int):
    """
    Record the number of FileUpload entities deleted during cleanup.

    Args:
        count: Number of entities deleted
    """
    try:
        db_cleanup_entities_deleted_counter.add(count)
    except Exception:
        pass


def record_db_cleanup_relationships_deleted(count: int):
    """
    Record the number of FileToUpload relationships deleted during cleanup.

    Args:
        count: Number of relationships deleted
    """
    try:
        db_cleanup_relationships_deleted_counter.add(count)
    except Exception:
        pass


def record_db_vacuum_run(duration_seconds: float, space_reclaimed_bytes: int):
    """
    Record that a VACUUM operation was performed.

    Args:
        duration_seconds: Time taken to complete the VACUUM operation
        space_reclaimed_bytes: Amount of space reclaimed in bytes
    """
    try:
        db_vacuum_runs_counter.add(1)
        db_vacuum_duration_hist.record(duration_seconds)
        if space_reclaimed_bytes > 0:
            db_vacuum_space_reclaimed_counter.add(space_reclaimed_bytes)
    except Exception:
        pass
