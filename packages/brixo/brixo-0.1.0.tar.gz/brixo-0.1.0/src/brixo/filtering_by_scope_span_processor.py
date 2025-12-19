import re
from opentelemetry.sdk.trace import SpanProcessor


class FilteringByScopeSpanProcessor(SpanProcessor):

    def __init__(self, delegate, allowed_scopes=None, blocked_scopes=None):
        self._delegate = delegate
        self.allowed_scopes = allowed_scopes or ()
        self.blocked_scopes = blocked_scopes or ()

    def on_end(self, span):
        scope = getattr(span, "instrumentation_scope", None)
        if scope is None:
            # older SDKs: fallback for backwards compatibility
            scope = getattr(span, "instrumentation_info", None)

        scope_name = getattr(scope, "name", None)

        # Filtering logic
        if (self.allowed_scopes and scope_name
                and all(not re.match(pattern, scope_name)
                        for pattern in self.allowed_scopes)):
            return
        if (self.blocked_scopes and scope_name and any(
                re.match(pattern, scope_name)
                for pattern in self.blocked_scopes)):
            return

        self._delegate.on_end(span)

    def shutdown(self):
        self._delegate.shutdown()

    def force_flush(self, timeout_millis=None):
        self._delegate.force_flush(timeout_millis)
