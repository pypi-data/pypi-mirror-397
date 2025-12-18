"""
ClarvynnLogProcessor - Log Filtering Based on Trace Sampling Decisions

This processor filters log records based on CPL sampling decisions, ensuring
logs and traces are consistently sampled together. Logs are often the most
expensive observability signal, so this provides significant cost savings.

KEY INSIGHT: Logs associated with exported traces are kept. Logs associated
with dropped traces are dropped. This ensures perfect correlation between
traces and logs while maintaining cost efficiency.

FLIGHT RECORDER:
Logs emitted during a request (before trace decision is known) are BUFFERED.
When the trace ends, the ClarvynnSpanProcessor flushes or clears the buffer.

COMPATIBILITY:
- OTel SDK 1.20-1.38: Uses LogData wrapper with log_record attribute
- OTel SDK 1.39+: Uses ReadWriteLogRecord directly (LogData removed)
"""

from typing import Any, Optional, Tuple

from clarvynn.logging import get_logger
from opentelemetry.sdk._logs import LogRecordProcessor
from opentelemetry.sdk._logs.export import LogExporter

# Handle OTel SDK version differences (1.39 removed LogData)
try:
    # OTel SDK 1.39+ - LogData removed, use ReadWriteLogRecord/ReadableLogRecord
    from opentelemetry.sdk._logs import ReadableLogRecord, ReadWriteLogRecord

    OTEL_139_PLUS = True
except ImportError:
    # OTel SDK 1.20-1.38 - LogData exists
    from opentelemetry.sdk._logs import LogData, LogRecord

    OTEL_139_PLUS = False

logger = get_logger("log_processor")


class ClarvynnLogProcessor(LogRecordProcessor):
    """
    Filters log records based on trace sampling decisions.

    Decision Logic:
    1. If log has trace_id (OTel automatically attaches it):
       - Check if trace was exported (query ClarvynnSpanProcessor cache)
       - If trace exported → export log
       - If trace dropped → drop log
       - If trace UNDECIDED (in-flight) → BUFFER log (Flight Recorder)
    2. If log has NO trace_id (background job, startup, etc.):
       - Apply base_rate sampling (same as traces)

    This ensures logs and traces are consistently sampled:
    - Error traces get their logs (100% capture)
    - Slow traces get their logs (100% capture)
    - Dropped traces don't get their logs (cost savings)

    ARCHITECTURE: Mirrors Clarvynn SDK's CPLLogExporter
    """

    def __init__(self, adapter, exporter: LogExporter, span_processor, log_buffer=None):
        """
        Initialize log processor with Clarvynn adapter and trace processor.

        Args:
            adapter: ProductionCPLAdapter that evaluates CPL conditions
            exporter: OTLP log exporter for sending logs
            span_processor: ClarvynnSpanProcessor for trace decision cache
            log_buffer: SharedRingBuffer for Flight Recorder (optional)
        """
        self.adapter = adapter
        self.exporter = exporter
        self.span_processor = span_processor
        self.log_buffer = log_buffer
        self.stats = {
            "total_logs": 0,
            "exported_logs": 0,
            "dropped_logs": 0,
            "buffered_logs": 0,
            "logs_with_trace": 0,
            "logs_without_trace": 0,
        }
        logger.info("ClarvynnLogProcessor initialized (correlated to trace sampling)")
        if self.log_buffer:
            logger.info("Flight Recorder enabled (Log Buffering active)")

    def emit(self, log_data: Any) -> None:
        """
        Called when a log record is emitted (OTel SDK < 1.22).

        Delegates to on_emit() for compatibility with older SDK versions.
        In older SDKs, the abstract method was named 'emit', not 'on_emit'.

        Args:
            log_data: LogData wrapper containing LogRecord
        """
        self.on_emit(log_data)

    def on_emit(self, log_record: Any) -> None:
        """
        Called when a log record is emitted (OTel SDK >= 1.22).

        Filters logs based on trace sampling decisions:
        - Logs with exported trace_id → export
        - Logs with dropped trace_id → drop
        - Logs with undecided trace_id → buffer
        - Logs without trace_id → apply base_rate

        Args:
            log_record: ReadWriteLogRecord (1.39+) or LogData (1.20-1.38)
        """
        self.stats["total_logs"] += 1

        try:
            # Handle OTel SDK version differences
            if OTEL_139_PLUS:
                # OTel 1.39+: log_record is ReadWriteLogRecord directly
                record = log_record
                exportable = log_record  # Can be exported directly
            else:
                # OTel 1.20-1.38: log_record is LogData wrapper
                record = log_record.log_record
                exportable = log_record  # Export the LogData wrapper

            should_export, should_buffer = self._evaluate_log(record)

            if should_export:
                self.exporter.export([exportable])
                self.stats["exported_logs"] += 1
            elif should_buffer and self.log_buffer:
                # Buffer the log record for later flush
                trace_id = getattr(record, "trace_id", 0)
                added = self.log_buffer.add_log(trace_id, exportable)
                if added:
                    self.stats["buffered_logs"] += 1
                else:
                    # Buffer full - drop log (fail-safe for memory)
                    self.stats["dropped_logs"] += 1
                    logger.warning(
                        f"Log buffer full for trace {self._format_trace_id(trace_id)} - dropping log"
                    )
            else:
                self.stats["dropped_logs"] += 1

        except Exception as e:
            # FAIL-SAFE: Never crash application due to log filtering
            # Export log on error to avoid losing critical data
            if OTEL_139_PLUS:
                self.exporter.export([log_record])
            else:
                self.exporter.export([log_record])
            self.stats["exported_logs"] += 1
            logger.error(f"Error in log processor: {e}")

    def _evaluate_log(self, record: Any) -> Tuple[bool, bool]:
        """
        Determine if log should be exported, buffered, or dropped.

        Returns:
            (should_export, should_buffer)
        """
        trace_id = getattr(record, "trace_id", None)

        if trace_id and trace_id != 0:
            # Log has trace_id (correlated to trace)
            self.stats["logs_with_trace"] += 1

            # Query span processor cache
            was_trace_exported = self.span_processor.was_trace_exported(trace_id)

            if was_trace_exported is None:
                # Trace not yet processed (in-flight)
                if self.log_buffer:
                    return False, True  # Buffer it!
                else:
                    # Fallback if no buffer configured (Old behavior: Fail-Safe Export)
                    return True, False

            # Follow trace decision (span has ended, decision is final)
            return was_trace_exported, False
        else:
            # Log has NO trace_id (background job, startup, etc.)
            self.stats["logs_without_trace"] += 1

            # Apply base_rate sampling
            should_export = self._check_base_rate_for_log(record)
            return should_export, False

    def _check_base_rate_for_log(self, record: Any) -> bool:
        """
        Apply base_rate sampling to logs without trace_id.

        Uses log timestamp hash as randomness source (similar to trace_id).

        Args:
            record: LogRecord to sample

        Returns:
            True if log passes base_rate sampling
        """
        base_rate = self.adapter.get_base_rate()

        if base_rate >= 1.0:
            return True
        if base_rate <= 0.0:
            return False

        # Use timestamp as randomness (hash to 56-bit range)
        timestamp_ns = getattr(record, "timestamp", None)
        if timestamp_ns is None:
            # No timestamp: default to exporting
            return True

        # Mix timestamp bits to get better distribution (even for small values)
        # Use simple multiplicative hash similar to MurmurHash
        mixed = (timestamp_ns * 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFF
        R = mixed
        T = int((1.0 - base_rate) * (2**56))

        return T <= R

    def _format_trace_id(self, trace_id: Optional[int]) -> str:
        """Format trace_id for logging."""
        if trace_id is None or trace_id == 0:
            return "None"
        return f"{trace_id:032x}"[:16] + "..."  # Show first 16 hex chars

    def shutdown(self) -> None:
        """Shutdown the log processor."""
        # Wrap logging in try/except to handle closed stream during Python shutdown
        try:
            logger.info("Shutting down ClarvynnLogProcessor")
            logger.info(f"  Total logs processed: {self.stats['total_logs']}")
            logger.info(f"  Exported logs: {self.stats['exported_logs']}")
            logger.info(f"  Dropped logs: {self.stats['dropped_logs']}")
            logger.info(f"  Buffered logs: {self.stats['buffered_logs']}")
            logger.info(f"  Logs with trace: {self.stats['logs_with_trace']}")
            logger.info(f"  Logs without trace: {self.stats['logs_without_trace']}")

            if self.stats["total_logs"] > 0:
                drop_rate = (self.stats["dropped_logs"] / self.stats["total_logs"]) * 100
                logger.info(f"  Log drop rate: {drop_rate:.1f}%")
        except (ValueError, OSError):
            # Stream may be closed during Python shutdown - this is expected
            pass

        self.exporter.shutdown()

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """Force flush pending logs."""
        try:
            logger.info("Force flushing logs")
        except (ValueError, OSError):
            # Stream may be closed during Python shutdown
            pass
        return self.exporter.force_flush(timeout_millis)
