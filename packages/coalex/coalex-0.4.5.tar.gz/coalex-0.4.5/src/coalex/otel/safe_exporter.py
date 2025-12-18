"""Safe OTLP exporter that suppresses errors gracefully."""

import logging
from typing import Sequence
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult
from opentelemetry.sdk.trace import ReadableSpan

logger = logging.getLogger(__name__)


class SafeOTLPSpanExporter(SpanExporter):
    """
    Wrapper around an OTLP exporter that catches and logs errors instead of raising them.

    This is useful when you want tracing to be best-effort and not affect the main
    application if the trace endpoint is unreachable.
    """

    def __init__(self, wrapped_exporter: SpanExporter, suppress_errors: bool = True):
        """
        Initialize the safe exporter.

        Args:
            wrapped_exporter: The actual OTLP exporter to wrap
            suppress_errors: Whether to suppress errors (default: True)
        """
        self.wrapped_exporter = wrapped_exporter
        self.suppress_errors = suppress_errors
        self._error_count = 0
        self._max_logged_errors = 3  # Only log first 3 errors to avoid log spam

    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        """
        Export spans, suppressing any errors.

        Args:
            spans: Sequence of spans to export

        Returns:
            SpanExportResult.SUCCESS if export succeeded or errors were suppressed,
            SpanExportResult.FAILURE otherwise
        """
        try:
            return self.wrapped_exporter.export(spans)
        except Exception as e:
            if not self.suppress_errors:
                raise

            self._error_count += 1

            # Only log the first few errors to avoid flooding logs
            if self._error_count <= self._max_logged_errors:
                logger.warning(
                    f"Failed to export {len(spans)} spans to Coalex (error #{self._error_count}): {type(e).__name__}: {str(e)}"
                )
                if self._error_count == self._max_logged_errors:
                    logger.warning(
                        f"Suppressing further span export errors (total so far: {self._error_count}). "
                        "Tracing will continue but spans may be lost if the endpoint is unreachable."
                    )

            # Return SUCCESS to indicate we've handled the error gracefully
            return SpanExportResult.SUCCESS

    def shutdown(self) -> None:
        """Shutdown the wrapped exporter."""
        try:
            self.wrapped_exporter.shutdown()
        except Exception as e:
            if not self.suppress_errors:
                raise
            logger.debug(f"Error during exporter shutdown: {e}")

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """Force flush the wrapped exporter."""
        try:
            return self.wrapped_exporter.force_flush(timeout_millis)
        except Exception as e:
            if not self.suppress_errors:
                raise
            logger.debug(f"Error during force flush: {e}")
            return False
