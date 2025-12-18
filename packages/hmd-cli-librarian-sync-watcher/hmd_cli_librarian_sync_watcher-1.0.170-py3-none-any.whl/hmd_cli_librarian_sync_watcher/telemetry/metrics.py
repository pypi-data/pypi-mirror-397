import os
import psutil
from pathlib import Path
from hmd_lib_telemetry.hmd_lib_telemetry import HmdMetric

# Metric name constants
FILE_UPSERTED = "file_upserted"
FILE_PROCESSING_DURATION = "file_processing_duration"
SYNC_CYCLE_DURATION = "sync_cycle_duration"
WATCH_EVENT_COUNT = "watch_event_count"
MEMORY_USAGE_BYTES = "memory_usage_bytes"
CPU_USAGE_PERCENT = "cpu_usage_percent"

# Initialize metric meters
sync_watcher_meter = HmdMetric("librarian_sync_watcher")

# Counters for file operations
file_upserted_counter = sync_watcher_meter.counter(
    FILE_UPSERTED, unit="1", description="Count of files upserted to database"
)

watch_event_counter = sync_watcher_meter.counter(
    WATCH_EVENT_COUNT, unit="1", description="Count of file watch events processed"
)

# Histograms for timing
file_processing_duration_hist = sync_watcher_meter.histogram(
    FILE_PROCESSING_DURATION,
    unit="s",
    description="Time taken to process a file",
)

sync_cycle_duration_hist = sync_watcher_meter.histogram(
    SYNC_CYCLE_DURATION, unit="s", description="Time taken to complete a sync cycle"
)

# Gauges for system metrics (CPU and memory only - DB size is reported by sync-manager)
memory_usage_gauge = sync_watcher_meter.up_down_counter(
    MEMORY_USAGE_BYTES,
    unit="By",
    description="Memory usage of the application in bytes",
)

cpu_usage_gauge = sync_watcher_meter.up_down_counter(
    CPU_USAGE_PERCENT, unit="%", description="CPU usage percentage of the application"
)


def record_file_upserted(count: int = 1):
    """Record that one or more files were upserted to the database."""
    file_upserted_counter.add(count)


def record_file_processing_duration(duration: float):
    """Record the time taken to process a file."""
    file_processing_duration_hist.record(duration)


def record_sync_cycle_duration(duration: float):
    """Record the time taken to complete a sync cycle."""
    sync_cycle_duration_hist.record(duration)


def record_watch_event_count(count: int = 1):
    """Record the number of watch events processed."""
    watch_event_counter.add(count)


def record_memory_usage():
    """Record the current memory usage of the application."""
    try:
        process = psutil.Process(os.getpid())
        memory_bytes = process.memory_info().rss
        memory_usage_gauge.add(
            memory_bytes - memory_usage_gauge._value
            if hasattr(memory_usage_gauge, "_value")
            else memory_bytes
        )
        memory_usage_gauge._value = memory_bytes
    except Exception:
        pass


def record_cpu_usage():
    """Record the current CPU usage percentage of the application."""
    try:
        process = psutil.Process(os.getpid())
        cpu_percent = process.cpu_percent(interval=0.1)
        cpu_usage_gauge.add(
            cpu_percent - cpu_usage_gauge._value
            if hasattr(cpu_usage_gauge, "_value")
            else cpu_percent
        )
        cpu_usage_gauge._value = cpu_percent
    except Exception:
        pass


def record_system_metrics(db_path: Path = None):
    """Record all system metrics (memory and CPU).

    Note: Database size is not recorded by the watcher as it shares the same
    database with the sync-manager, which already reports this metric.
    """
    record_memory_usage()
    record_cpu_usage()
