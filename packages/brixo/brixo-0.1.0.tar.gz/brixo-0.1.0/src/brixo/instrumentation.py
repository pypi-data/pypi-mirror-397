from typing import Callable, Optional, TypedDict

from opentelemetry.trace.span import NonRecordingSpan, Span
from brixo.brixo_tracer_provider import (
    BrixoTracerProvider, )
from brixo.filtering_by_scope_span_processor import (
    FilteringByScopeSpanProcessor, )
from openinference.instrumentation.langchain import LangChainInstrumentor
from traceloop.sdk import Traceloop
from traceloop.sdk.decorators import TraceloopSpanKindValues, workflow, F
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry import trace
from os import getenv
import weakref

OPENINFERENCE_SCOPE_PATTERNS = ("openinference.instrumentation", )
TRACELOOP_SCOPE_PATTERNS = (
    "opentelemetry.instrumentation",
    # This one is necessary to send
    # the top span that will be created using the interaction decorator.
    #
    # The top span can be filtered out when sending traces to Phoenix(Openinference)
    # but, on Traceloop, filtering the top span will break the trace presentation
    "traceloop.tracer")

ROOT_SPAN_TRACE_ID_REGISTRY: weakref.WeakValueDictionary[int, Span] = (
    weakref.WeakValueDictionary())


class Brixo:
    """Entry point for initializing Brixo instrumentation over Opentelemetry"""

    @staticmethod
    def init(app_name: str,
             api_key=None,
             filter_openinference_spans=True,
             filter_traceloop_spans=True):
        """Sets up OpenTelemetry export with the provided credentials and enables
        auto-instrumentation so application traces are captured and sent.

        Args:
            app_name: Logical service name reported in traces.
            api_key: Brixo API key; falls back to BRIXO_API_KEY env var.
            filter_openinference_spans: Whether to drop OpenInference spans on export.
            filter_traceloop_spans: Whether to drop Traceloop spans on export.
        """

        filter_scopes = ()
        if filter_openinference_spans:
            filter_scopes += OPENINFERENCE_SCOPE_PATTERNS

        if filter_traceloop_spans:
            filter_scopes += TRACELOOP_SCOPE_PATTERNS

        resource = Resource(attributes={"brixo.app_name": app_name})
        tracer_provider = BrixoTracerProvider(
            resource=resource, default_blocked_scopes=filter_scopes)
        trace.set_tracer_provider(tracer_provider)

        brixo_api_key = api_key or getenv("BRIXO_API_KEY")
        brixo_otel_endpoint = getenv(
            "BRIXO_OTLP_TRACES_ENDPOINT"
        ) or "https://otel.brixo.com:4318/v1/traces"

        headers = {"Brixo-Auth": f"Bearer {brixo_api_key}"}
        batch_span_processor = BatchSpanProcessor(
            OTLPSpanExporter(endpoint=brixo_otel_endpoint, headers=headers))

        processor = FilteringByScopeSpanProcessor(
            batch_span_processor,
            allowed_scopes=OPENINFERENCE_SCOPE_PATTERNS +
            TRACELOOP_SCOPE_PATTERNS)

        LangChainInstrumentor().instrument()

        if filter_traceloop_spans:
            Traceloop.init(processor=processor)
        else:
            tracer_provider.add_span_processor(processor)


def interaction(
    name: Optional[str] = None,
    version: Optional[int] = None,
    method_name: Optional[str] = None,
) -> Callable[[F], F]:
    return workflow(
        name=name,
        version=version,
        method_name=method_name,
        tlp_span_kind=TraceloopSpanKindValues.WORKFLOW,
    )


class CustomerContext(TypedDict, total=False):
    id: str
    name: str


class UserContext(TypedDict, total=False):
    id: str
    name: str
    role: str
    email: str


def begin_context(customer: CustomerContext | None = None,
                  user: UserContext | None = None,
                  session_id: str | None = None,
                  metadata: dict | None = None,
                  input: str | None = None):
    """Defines the root span that will hold context attributes and add 
    customer, user, session, and metadata attributes to the root span.

    Args:
        customer: Identifiers and details for the current customer/org.
        user: Identifiers and details for the acting end-user.
        session_id: Session identifier to correlate related interactions.
        metadata: Optional extra key/value pairs to append under `brixo.metadata.*`.
        input: Raw input payload for the interaction.
    """
    span = _get_root_span()

    if not span:
        return

    attributes = {}

    if customer is not None:
        for key, value in customer.items():
            attributes[f"brixo.customer.{key}"] = value

    if user is not None:
        for key, value in user.items():
            attributes[f"brixo.user.{key}"] = value

    if session_id is not None:
        attributes["brixo.session_id"] = session_id

    if metadata is not None:
        for key, value in metadata.items():
            attributes[f"brixo.metadata.{key}"] = value

    if input is not None:
        attributes['brixo.input'] = input

    span.set_attributes(attributes)


def update_context(output: str | None = None, metadata: dict | None = None):
    """Append output and metadata attributes to the root span.

    Args:
        output: Raw output payload for the interaction.
        metadata: Optional extra key/value pairs to append under `brixo.metadata.*`.
    """
    span = _get_root_span()

    if not span: return

    attributes = {}

    if metadata is not None:
        for key, value in metadata.items():
            attributes[f"brixo.metadata.{key}"] = value

    if output is not None:
        attributes['brixo.output'] = output

    span.set_attributes(attributes)


def _get_root_span():
    span = trace.get_current_span()

    if type(span) == NonRecordingSpan: return None

    trace_id = span.context.trace_id

    if root_span := ROOT_SPAN_TRACE_ID_REGISTRY.get(trace_id):
        return root_span

    if span.parent: return None

    # This Span instance will have strong reference in the decorated function stack.
    # Once there is no strong reference to it, the key will be removed from the
    # ROOT_SPAN_TRACE_ID_REGISTRY dictionary
    return ROOT_SPAN_TRACE_ID_REGISTRY.setdefault(trace_id, span)
