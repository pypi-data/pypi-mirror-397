"""
ClarvynnSpanProcessor - Deferred Head Sampling Processor for Clarvynn.

This implements OpenTelemetry's SpanProcessor interface and evaluates
CPL policies AFTER spans complete, allowing intelligent decisions based
on actual request outcomes (status_code, duration, errors).

KEY INSIGHT: Unlike Sampler (head-based), SpanProcessor (tail-based)
can see the ACTUAL results of requests, enabling:
- 100% error capture
- 100% slow request capture
- Intelligent filtering based on real outcomes

FLIGHT RECORDER:
When a span ends, we check if there are buffered logs for this trace.
- If span KEPT -> Flush logs (Export)
- If span DROPPED -> Clear logs (Drop)
"""

import threading
from collections import OrderedDict
from typing import Optional

from clarvynn.logging import get_logger
from opentelemetry import context as otel_context
from opentelemetry import trace
from opentelemetry.context import Context
from opentelemetry.sdk.trace import ReadableSpan, SpanProcessor
from opentelemetry.sdk.trace.export import SpanExporter

logger = get_logger("span_processor")


class ClarvynnSpanProcessor(SpanProcessor):
    """
    Deferred Head Sampling processor that evaluates CPL policies.

    This processor is added to TracerProvider and is called:
    - on_start(): When span starts (we just track it)
    - on_end(): When span completes (THIS IS WHERE WE DECIDE)

    ARCHITECTURE: Mirrors Clarvynn SDK's CPLBatchSpanProcessor
    """

    def __init__(self, adapter, exporter: SpanExporter, log_buffer=None, log_exporter=None):
        """
        Initialize processor with Clarvynn adapter and TraceState exporter.

        Args:
            adapter: ProductionCPLAdapter that evaluates CPL conditions
            exporter: ClarvynnTraceStateExporter (wraps OTLP)
            log_buffer: SharedRingBuffer for Flight Recorder (optional)
            log_exporter: LogExporter to flush buffered logs to (optional)
        """
        self.adapter = adapter
        self.exporter = exporter
        self.log_buffer = log_buffer
        self.log_exporter = log_exporter
        self.stats = {
            "total_spans": 0,
            "exported_spans": 0,
            "dropped_spans": 0,
            "critical_spans": 0,
            "upstream_forced": 0,
            "flushed_logs": 0,
            "cleared_logs": 0,
        }

        # Trace decision cache for log filtering
        # Maps trace_id -> bool (True = exported, False = dropped)
        # Using OrderedDict for LRU-like eviction
        self._trace_decisions = OrderedDict()
        self._max_cache_size = 10000
        self._cache_lock = threading.Lock()  # Protects _trace_decisions

        logger.info(
            "ClarvynnSpanProcessor initialized (Deferred Head Sampling + W3C TraceContext Level 2)"
        )
        if self.log_buffer:
            logger.info("Flight Recorder enabled (Log Flushing active)")

    def on_start(self, span: ReadableSpan, parent_context: Optional[Context] = None):
        """
        Called when span starts.

        At this point, the request hasn't executed yet, so we don't
        have status_code, duration, or error information.

        We just track that the span started.
        """
        self.stats["total_spans"] += 1
        logger.debug(f"Span started: {span.name}")

    def on_end(self, span: ReadableSpan):
        """
        CRITICAL: Called when span ENDS (request completed)

        NOW we have everything we need:
        - status_code (200, 404, 500, etc.)
        - duration (how long request took)
        - error information (if exception occurred)
        - all span attributes

        This is where Clarvynn makes the intelligent decision!
        """

        try:
            attrs = self._extract_span_attributes(span)
            logger.debug(
                f"  Extracted attributes: method={attrs.get('method', 'N/A')}, path={attrs.get('path', 'N/A')}, status_code={attrs.get('status_code', 'N/A')}, duration={attrs.get('duration', 'N/A')}ms"
            )

            should_keep, reason, is_critical = self._should_export_span(span, attrs)

            # Store trace decision in cache for log filtering
            self._record_trace_decision(span.context.trace_id, should_keep)

            # FLIGHT RECORDER LOGIC
            if self.log_buffer:
                self._handle_buffered_logs(span.context.trace_id, should_keep)

            if should_keep:
                # Mark span as critical for TraceState exporter
                if is_critical:
                    self._mark_span_critical(span)
                    self.stats["critical_spans"] += 1

                self.exporter.export([span])
                self.stats["exported_spans"] += 1

                if reason.startswith("condition:"):
                    logger.info(
                        f"✅ CPL condition '{reason}' triggered - exporting critical span: {span.name}"
                    )
                elif reason == "upstream_critical":
                    logger.info(
                        f"✅ Upstream critical trace (ot=th:0) - exporting span: {span.name}"
                    )
                elif reason == "upstream_threshold":
                    logger.info(f"✅ Upstream threshold match - exporting span: {span.name}")
                else:
                    logger.info(f"✅ Exported span: {span.name} (reason: {reason})")
            else:
                self.stats["dropped_spans"] += 1
                logger.debug(f"🗑️ Dropped span: {span.name}")

        except Exception as e:
            logger.error(f"Error in span evaluation: {e}")
            self.exporter.export([span])
            self.stats["exported_spans"] += 1

            # Fail-safe: Flush logs on error
            if self.log_buffer:
                self._handle_buffered_logs(span.context.trace_id, True)

    def _handle_buffered_logs(self, trace_id: int, should_keep: bool):
        """
        Flush or clear buffered logs for the given trace.
        """
        if not trace_id:
            return

        if should_keep:
            # Trace kept -> Flush logs to exporter
            logs = self.log_buffer.get_and_clear(trace_id)
            if logs and self.log_exporter:
                self.log_exporter.export(logs)
                self.stats["flushed_logs"] += len(logs)
                # logger.debug(f"Flushed {len(logs)} buffered logs for trace {trace_id:032x}")
        else:
            # Trace dropped -> Clear logs (Drop)
            # We can just clear, but let's count them for stats if needed (requires get_and_clear)
            # For performance, just clear() is faster if we don't need exact count
            # But let's get count for observability during beta
            logs = self.log_buffer.get_and_clear(trace_id)
            if logs:
                self.stats["cleared_logs"] += len(logs)
                # logger.debug(f"Cleared {len(logs)} buffered logs for trace {trace_id:032x}")

    def _extract_span_attributes(self, span: ReadableSpan) -> dict:
        """
        Extract complete attributes from finished span.

        Returns:
            dict with all attributes needed for CPL evaluation
        """
        attrs = {}

        if span.attributes:
            attrs.update(dict(span.attributes))

        attrs["span.name"] = span.name
        attrs["trace_id"] = span.context.trace_id

        if span.status:
            attrs["status_code"] = span.status.status_code.value

        if span.start_time and span.end_time:
            duration_ms = (span.end_time - span.start_time) / 1_000_000
            attrs["duration"] = duration_ms

        if "http.status_code" in attrs:
            attrs["status_code"] = attrs["http.status_code"]

        if "http.route" in attrs:
            attrs["path"] = attrs["http.route"]

        if "http.target" in attrs and "path" not in attrs:
            attrs["path"] = attrs["http.target"]

        if "http.method" in attrs:
            attrs["method"] = attrs["http.method"]

        if "http.url" in attrs and "path" not in attrs:
            # Extract path from full URL
            from urllib.parse import urlparse

            parsed = urlparse(attrs["http.url"])
            attrs["path"] = parsed.path

        return attrs

    def _should_export_span(self, span: ReadableSpan, attrs: dict) -> tuple:
        """
        Evaluate CPL policy to decide if span should be exported.

        W3C TraceContext Level 2 Priority Order:
        1. CPL conditions (errors, slow, critical paths) → ALWAYS export + mark critical
        2. Upstream TraceState (distributed consistency):
           - ot=th:0 → Force export + mark critical
           - ot=th:XXX → Compare with our threshold
        3. Base rate (random sampling) → Export X% of remaining

        Returns:
            (should_export: bool, reason: str, is_critical: bool)
        """

        # Priority 1: CPL Conditions (highest priority)
        for condition in self.adapter.get_conditions():
            if condition.evaluate(attrs):
                return (True, f"condition:{condition.name}", True)

        # Priority 2: Upstream TraceState
        upstream_threshold = self._read_upstream_threshold(span)

        if upstream_threshold is not None:
            if upstream_threshold == 0:
                # Critical trace from upstream (ot=th:0)
                # Force 100% sampling and mark as critical
                self.stats["upstream_forced"] += 1
                return (True, "upstream_critical", True)

            # Check if trace_id passes upstream threshold
            trace_id = attrs.get("trace_id", 0)
            R = trace_id & 0xFFFFFFFFFFFFFF  # Last 56 bits

            if upstream_threshold <= R:
                # Upstream wants this sampled
                return (True, "upstream_threshold", False)

        # Priority 3: Our base rate
        trace_id = attrs.get("trace_id", 0)

        if self._check_base_rate(trace_id):
            return (True, "base_rate", False)

        return (False, "dropped", False)

    def _read_upstream_threshold(self, span: ReadableSpan) -> Optional[int]:
        """
        Read W3C TraceContext Level 2 threshold from upstream service.

        Checks the span's context for TraceState with OpenTelemetry vendor key:
        - ot=th:0 → Critical trace (100% sampling)
        - ot=th:XXX → Threshold value for consistent sampling

        Returns:
            Threshold as integer (0 for critical), or None if not set
        """
        try:
            trace_state = span.context.trace_state

            if not trace_state:
                return None

            # Get OpenTelemetry vendor key value
            ot_value = trace_state.get("ot")

            if not ot_value:
                return None

            # Parse threshold: "th:0" or "th:e666666666666"
            if not ot_value.startswith("th:"):
                return None

            threshold_hex = ot_value[3:]  # Remove "th:" prefix

            if not threshold_hex:
                return None

            # Convert hex to integer
            threshold = int(threshold_hex, 16)

            logger.debug(f"Upstream threshold: {threshold_hex} ({threshold})")
            return threshold

        except (ValueError, AttributeError) as e:
            logger.debug(f"Failed to parse upstream threshold: {e}")
            return None

    def _mark_span_critical(self, span: ReadableSpan):
        """
        Mark span as critical for TraceState injection.

        The TraceStateExporter will read this attribute and inject
        ot=th:0 to force 100% downstream sampling.

        NOTE: We can't modify ReadableSpan directly, but we CAN set
        attributes on the underlying span if it's still mutable.
        For export-only marking, the exporter will re-evaluate conditions.
        """
        # Try to mark the span if it's still mutable (unlikely in on_end)
        # The exporter will re-evaluate CPL conditions to be safe
        try:
            if hasattr(span, "set_attribute"):
                span.set_attribute("clarvynn.critical", True)
        except Exception:
            # Expected - ReadableSpan is immutable
            # Exporter will re-evaluate conditions
            pass

    def _check_base_rate(self, trace_id: int) -> bool:
        """
        Check if trace_id passes base rate sampling.

        Uses W3C TraceContext Level 2 compliant sampling:
        - Extract last 56 bits of trace_id (random)
        - Compare with threshold derived from base_rate
        """
        base_rate = self.adapter.get_base_rate()

        if base_rate >= 1.0:
            return True
        if base_rate <= 0.0:
            return False

        R = trace_id & 0xFFFFFFFFFFFFFF
        T = int((1.0 - base_rate) * (2**56))

        return T <= R

    def _record_trace_decision(self, trace_id: int, was_exported: bool):
        """
        Record whether a trace was exported or dropped.

        This cache is used by ClarvynnLogProcessor to filter logs
        based on trace sampling decisions, ensuring logs and traces
        are consistently sampled together.

        Args:
            trace_id: OpenTelemetry trace ID
            was_exported: True if trace was exported, False if dropped
        """
        with self._cache_lock:
            # Add to cache (OrderedDict maintains insertion order)
            self._trace_decisions[trace_id] = was_exported

            # Evict oldest 10% if cache is full (LRU-like behavior)
            if len(self._trace_decisions) > self._max_cache_size:
                evict_count = self._max_cache_size // 10
                for _ in range(evict_count):
                    self._trace_decisions.popitem(last=False)  # Remove oldest
                logger.debug(f"Evicted {evict_count} old trace decisions from cache")

    def was_trace_exported(self, trace_id: int) -> Optional[bool]:
        """
        Check if a trace was exported or dropped.

        Used by ClarvynnLogProcessor to filter logs based on trace decisions.

        Args:
            trace_id: OpenTelemetry trace ID

        Returns:
            True if trace was exported
            False if trace was dropped
            None if trace_id not in cache (trace not yet processed)
        """
        with self._cache_lock:
            return self._trace_decisions.get(trace_id)

    def shutdown(self):
        """Shutdown the processor."""
        logger.info("Shutting down ClarvynnSpanProcessor")
        logger.info(f"  Trace decision cache size: {len(self._trace_decisions)}")
        if self.log_buffer:
            logger.info(f"  Flushed logs: {self.stats['flushed_logs']}")
            logger.info(f"  Cleared logs: {self.stats['cleared_logs']}")
        self.exporter.shutdown()

    def force_flush(self, timeout_millis: int = 30000):
        """Force flush pending spans."""
        logger.info("Force flushing spans")
        return self.exporter.force_flush(timeout_millis)
