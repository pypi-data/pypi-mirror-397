import os

from typing import Optional

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor


class ArcbeamLangConnector:
    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        self.base_url = base_url or os.getenv("ARCBEAM_BASE_URL") or "https://platform.arcbeam.ai/api/v0/traces"
        self.api_key = api_key or os.getenv("ARCBEAM_API_KEY") or ""

    def init(self, project_id: Optional[str] = None):
        os.environ["LANGSMITH_OTEL_ENABLED"] = "true"
        os.environ["LANGSMITH_TRACING"] = "true"
        os.environ["LANGSMITH_OTEL_ONLY"] = "true"

        resources = {"arcbeam.framework": "langchain"}

        if project_id:
            resources["arcbeam.project_id"] = project_id

        # Configure the OTLP exporter for your custom endpoint
        provider = TracerProvider(resource=Resource.create(resources))
        otlp_exporter = OTLPSpanExporter(
            # Point to the /api/v1/traces endpoint
            endpoint=self.base_url,
            # Add any required headers for authentication if needed
            headers={"arcbeam-api-key": self.api_key},
        )

        processor = SimpleSpanProcessor(otlp_exporter)
        provider.add_span_processor(processor)
        trace.set_tracer_provider(provider)

        return trace
