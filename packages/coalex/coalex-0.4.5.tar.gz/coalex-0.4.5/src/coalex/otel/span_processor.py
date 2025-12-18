"""Span processor to propagate Coalex attributes from parent to child spans."""

import logging
from opentelemetry.sdk.trace import SpanProcessor, Span, ReadableSpan
from opentelemetry import trace, context

logger = logging.getLogger(__name__)


class CoalexAttributePropagator(SpanProcessor):
    """
    Span processor that propagates Coalex attributes from parent to child spans.

    This ensures that attributes like session.id and prompt.version set on a parent
    span are automatically copied to all child spans (like LLM calls).
    """

    ATTRIBUTES_TO_PROPAGATE = [
        "session.id",
        "prompt.version",
        "account_id",
        "coalex.agent_id",
    ]

    def on_start(self, span: Span, parent_context=None):
        """
        Called when a span starts. Copies Coalex attributes from parent span.

        Args:
            span: The span that is starting
            parent_context: The parent context (contains parent span)
        """
        if not span.is_recording():
            return

        # Get parent span from context
        ctx = parent_context if parent_context is not None else context.get_current()
        parent_span = trace.get_current_span(ctx)

        if not parent_span or not hasattr(parent_span, 'attributes'):
            return

        # Copy Coalex attributes from parent to child
        copied_count = 0
        for attr_name in self.ATTRIBUTES_TO_PROPAGATE:
            # Check if parent has this attribute
            parent_value = parent_span.attributes.get(attr_name)
            if parent_value is not None:
                # Only set if child doesn't already have it
                if not hasattr(span, 'attributes') or attr_name not in span.attributes:
                    span.set_attribute(attr_name, parent_value)
                    copied_count += 1
                    logger.debug(f"Propagated {attr_name}={parent_value} from parent to child span '{span.name}'")

        if copied_count > 0:
            logger.debug(f"Propagated {copied_count} Coalex attributes to span '{span.name}'")

    def on_end(self, span: ReadableSpan):
        """Called when a span ends. No action needed."""
        pass

    def shutdown(self):
        """Called when the processor is shutdown. No action needed."""
        pass

    def force_flush(self, timeout_millis=30000):
        """Called to flush any buffered spans. No action needed."""
        pass
