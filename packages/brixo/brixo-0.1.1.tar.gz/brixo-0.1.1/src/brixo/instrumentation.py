import contextlib
import logging
import weakref
from collections.abc import Callable
from importlib import metadata
from os import devnull, getenv
from typing import TypedDict

from colorama import Fore
from openinference.instrumentation.langchain import LangChainInstrumentor
from openinference.instrumentation.openai import OpenAIInstrumentor
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace.span import NonRecordingSpan, Span
from traceloop.sdk import Traceloop
from traceloop.sdk.decorators import F, TraceloopSpanKindValues, workflow

from brixo.brixo_tracer_provider import (
    BrixoTracerProvider,
)
from brixo.filtering_by_scope_span_processor import (
    FilteringByScopeSpanProcessor,
)

OPENINFERENCE_SCOPE_PATTERNS = ("openinference.instrumentation",)
TRACELOOP_SCOPE_PATTERNS = (
    "opentelemetry.instrumentation",
    # This one is necessary to send
    # the top span that will be created using the interaction decorator.
    #
    # The top span can be filtered out when sending traces to Phoenix(Openinference)
    # but, on Traceloop, filtering the top span will break the trace presentation
    "traceloop.tracer",
)

ROOT_SPAN_TRACE_ID_REGISTRY: weakref.WeakValueDictionary[int, Span] = weakref.WeakValueDictionary()

REQUIRED_ROOT_SPAN_ATTRIBUTES = {
    "brixo.account.id": "account.id",
    "brixo.account.name": "account.name",
    "brixo.user.id": "user.id",
    "brixo.user.name": "user.name",
    "brixo.session_id": "session_id",
    "brixo.input": "input",
    "brixo.output": "output",
}

_OTEL_AUTH_FILTER_INSTALLED = {"value": False}
_OTEL_AUTH_FAILURE_LOGGED = {"value": False}


class _OtelAuthFailureFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if "Failed to export span batch code" not in str(record.msg):
            return True

        status_code = None
        if isinstance(record.args, tuple) and record.args:
            status_code = record.args[0]
        elif record.args:
            status_code = record.args

        if status_code not in (401, 403):
            return True

        if not _OTEL_AUTH_FAILURE_LOGGED["value"]:
            logging.getLogger(__name__).error(
                "%s[Brixo] Authentication Failure: Please check your BRIXO_API_KEY environment "
                "variable.%s",
                Fore.RED,
                Fore.RESET,
            )
            _OTEL_AUTH_FAILURE_LOGGED["value"] = True

        return False


def _ensure_otel_auth_filter() -> None:
    if _OTEL_AUTH_FILTER_INSTALLED["value"]:
        return

    logging.getLogger("opentelemetry.exporter.otlp.proto.http.trace_exporter").addFilter(
        _OtelAuthFailureFilter()
    )
    _OTEL_AUTH_FILTER_INSTALLED["value"] = True


class Brixo:
    """Entry point for initializing Brixo instrumentation over Opentelemetry"""

    @staticmethod
    def init(
        app_name: str,
        environment: str,
        api_key=None,
        filter_openinference_spans=True,
        filter_traceloop_spans=True,
    ):
        """Sets up OpenTelemetry export with the provided credentials and enables
        auto-instrumentation so application traces are captured and sent.

        Args:
            app_name: Logical service name reported in traces.
            environment: Deployment environment label for this service instance (e.g., "local",
                "dev", "staging", "prod"). Used to tag traces for filtering and comparison across
                environments.
            api_key: Brixo API key; falls back to BRIXO_API_KEY env var.
            filter_openinference_spans: Whether to drop OpenInference spans on export.
            filter_traceloop_spans: Whether to drop Traceloop spans on export.
        """

        filter_scopes = ()
        if filter_openinference_spans:
            filter_scopes += OPENINFERENCE_SCOPE_PATTERNS

        if filter_traceloop_spans:
            filter_scopes += TRACELOOP_SCOPE_PATTERNS

        try:
            sdk_version = metadata.version("brixo")
        except metadata.PackageNotFoundError:
            sdk_version = "unknown"

        resource = Resource(
            attributes={
                "brixo.app_name": app_name,
                "brixo.environment": environment,
                "brixo.sdk.version": sdk_version,
            }
        )
        tracer_provider = BrixoTracerProvider(
            resource=resource, default_blocked_scopes=filter_scopes
        )
        trace.set_tracer_provider(tracer_provider)

        brixo_api_key = api_key or getenv("BRIXO_API_KEY")
        if not brixo_api_key:
            logging.getLogger(__name__).error(
                "%s[Brixo] BRIXO_API_KEY environment variable not set. Please set your "
                "Brixo API Key before continuing.%s",
                Fore.RED,
                Fore.RESET,
            )
        brixo_otel_endpoint = (
            getenv("BRIXO_OTLP_TRACES_ENDPOINT") or "https://otel.brixo.com:4318/v1/traces"
        )

        headers = {"Brixo-Auth": f"Bearer {brixo_api_key}"}
        _ensure_otel_auth_filter()
        batch_span_processor = BatchSpanProcessor(
            OTLPSpanExporter(endpoint=brixo_otel_endpoint, headers=headers)
        )

        processor = FilteringByScopeSpanProcessor(
            batch_span_processor,
            allowed_scopes=OPENINFERENCE_SCOPE_PATTERNS + TRACELOOP_SCOPE_PATTERNS,
            required_root_span_attributes=REQUIRED_ROOT_SPAN_ATTRIBUTES,
        )

        LangChainInstrumentor().instrument()
        OpenAIInstrumentor().instrument()

        if filter_traceloop_spans:
            # Temporarily redirects Traceloop prints to /dev/null
            with contextlib.redirect_stdout(open(devnull, "w")):
                Traceloop.init(processor=processor)
        else:
            tracer_provider.add_span_processor(processor)

    @staticmethod
    def interaction(
        name: str | None = None,
    ) -> Callable[[F], F]:
        """Mark ONE bounded user interaction (one request → one response) so Brixo can group
        spans/attributes into a single trace and flush it when this function returns.

        Args:
            name: Interaction name
        """
        return workflow(
            name=name,
            version=None,
            method_name=None,
            tlp_span_kind=TraceloopSpanKindValues.WORKFLOW,
        )

    @staticmethod
    def begin_context(  # noqa: PLR0913
        account: "AccountContext | None" = None,
        user: "UserContext | None" = None,
        session_id: str | None = None,
        metadata: dict | None = None,
        input: str | None = None,
        output: str | None = None,
    ):
        """Defines the root span that will hold context attributes and add
        account, user, session, metadata, input, and output attributes to the root span.

        Args:
            account: Identifiers and details for the current account/org.
            user: Identifiers and details for the acting end-user.
            session_id: Session identifier to correlate related interactions.
            metadata: Optional extra key/value pairs to append under `brixo.metadata.*`.
            input: Input of the interaction.
            output: Output of the interaction.
        """
        span = _get_root_span()

        if not span:
            return

        _set_context_attributes(
            span=span,
            account=account,
            user=user,
            session_id=session_id,
            metadata=metadata,
            input=input,
            output=output,
        )

    @staticmethod
    def update_context(  # noqa: PLR0913
        account: "AccountContext | None" = None,
        user: "UserContext | None" = None,
        session_id: str | None = None,
        metadata: dict | None = None,
        input: str | None = None,
        output: str | None = None,
    ):
        """Update root span context attributes.

        Args:
            account: Identifiers and details for the current account/org.
            user: Identifiers and details for the acting end-user.
            session_id: Session identifier to correlate related interactions.
            metadata: Optional extra key/value pairs to append under `brixo.metadata.*`.
            input: Input of the interaction.
            output: Output of the interaction.
        """
        span = _get_root_span()

        if not span:
            return

        _set_context_attributes(
            span=span,
            account=account,
            user=user,
            session_id=session_id,
            metadata=metadata,
            input=input,
            output=output,
        )

    @staticmethod
    def end_context(  # noqa: PLR0913
        account: "AccountContext | None" = None,
        user: "UserContext | None" = None,
        session_id: str | None = None,
        metadata: dict | None = None,
        input: str | None = None,
        output: str | None = None,
    ):
        """End the root span and update context attributes.

        Args:
            account: Identifiers and details for the current account/org.
            user: Identifiers and details for the acting end-user.
            session_id: Session identifier to correlate related interactions.
            metadata: Optional extra key/value pairs to append under `brixo.metadata.*`.
            input: Input of the interaction.
            output: Output of the interaction.
        """
        span = _get_root_span()

        if not span:
            return

        _set_context_attributes(
            span=span,
            account=account,
            user=user,
            session_id=session_id,
            metadata=metadata,
            input=input,
            output=output,
        )


class AccountContext(TypedDict, total=False):
    id: str
    name: str
    logo_url: str
    website_url: str


class UserContext(TypedDict, total=False):
    id: str
    name: str
    email: str


def _set_context_attributes(  # noqa: PLR0913
    span: Span,
    account: AccountContext | None = None,
    user: UserContext | None = None,
    session_id: str | None = None,
    metadata: dict | None = None,
    input: str | None = None,
    output: str | None = None,
):
    attributes = {}

    if account is not None:
        for key, value in account.items():
            attributes[f"brixo.account.{key}"] = value

    if user is not None:
        for key, value in user.items():
            attributes[f"brixo.user.{key}"] = value

    if session_id is not None:
        attributes["brixo.session_id"] = session_id

    if metadata is not None:
        for key, value in metadata.items():
            attributes[f"brixo.metadata.{key}"] = value

    if input is not None:
        attributes["brixo.input"] = input

    if output is not None:
        attributes["brixo.output"] = output

    span.set_attributes(attributes)


def _get_root_span():
    span = trace.get_current_span()

    if isinstance(span, NonRecordingSpan):
        return None

    trace_id = span.context.trace_id

    if root_span := ROOT_SPAN_TRACE_ID_REGISTRY.get(trace_id):
        return root_span

    if span.parent:
        return None

    # This Span instance will have strong reference in the decorated function stack.
    # Once there is no strong reference to it, the key will be removed from the
    # ROOT_SPAN_TRACE_ID_REGISTRY dictionary
    return ROOT_SPAN_TRACE_ID_REGISTRY.setdefault(trace_id, span)
