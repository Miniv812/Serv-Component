import json
import logging
import os
from datetime import datetime, timezone

from flask import Flask
from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (
    OTLPMetricExporter,
)
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.grpc import (
    GrpcInstrumentorClient,
    GrpcInstrumentorServer,
)
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

_grpc_client_instrumented = False
_grpc_server_instrumented = False


class OTelTraceContextFilter(logging.Filter):
    """Фільтр для кореляції OpenTelemetry Trace ID та Span ID у JSON-логах."""

    def filter(self, record: logging.LogRecord) -> bool:
        span = trace.get_current_span()
        if span and span.get_span_context().is_valid:
            ctx = span.get_span_context()
            record.trace_id = f"{ctx.trace_id:032x}"
            record.span_id = f"{ctx.span_id:016x}"
        else:
            record.trace_id = "0"
            record.span_id = "0"
        return True


class JsonLogFormatter(logging.Formatter):
    """Форматер структурованих логів у форматі JSON з прив'язкою до OTel."""

    def __init__(self, service_name: str) -> None:
        super().__init__()
        self.service_name = service_name

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "service": self.service_name,
            "logger": record.name,
            "message": record.getMessage(),
            "trace_id": getattr(record, "trace_id", "0"),
            "span_id": getattr(record, "span_id", "0"),
        }
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry, ensure_ascii=False)


def setup_json_logging(service_name: str) -> None:
    """Налаштовує вивід усіх логів застосунку у форматі JSON з trace_id."""
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    handler.addFilter(OTelTraceContextFilter())
    handler.setFormatter(JsonLogFormatter(service_name))

    root_logger.handlers.clear()
    root_logger.addHandler(handler)


def init_telemetry(
    service_name: str,
    app: Flask | None = None,
    testing: bool = False,
) -> None:
    """Ініціалізує OpenTelemetry Tracing, Metrics, JSON-логи та інструментування."""
    setup_json_logging(service_name)
    resource = Resource.create({"service.name": service_name})

    tracer_provider = TracerProvider(resource=resource)
    if not testing:
        otlp_endpoint = os.getenv(
            "OTEL_EXPORTER_OTLP_ENDPOINT",
            "http://otel-collector:4317",
        )
        trace_exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
        tracer_provider.add_span_processor(BatchSpanProcessor(trace_exporter))

        metric_reader = PeriodicExportingMetricReader(
            OTLPMetricExporter(endpoint=otlp_endpoint, insecure=True),
            export_interval_millis=5000,
        )
        meter_provider = MeterProvider(
            resource=resource,
            metric_readers=[metric_reader],
        )
        metrics.set_meter_provider(meter_provider)

    trace.set_tracer_provider(tracer_provider)

    if app is not None:
        FlaskInstrumentor().instrument_app(app)


def instrument_grpc_server() -> None:
    """Вмикає екстракцію W3C Trace Context на стороні gRPC-сервера."""
    global _grpc_server_instrumented
    if not _grpc_server_instrumented:
        GrpcInstrumentorServer().instrument()
        _grpc_server_instrumented = True


def instrument_grpc_client() -> None:
    """Вмикає ін'єкцію W3C Trace Context у Metadata на стороні gRPC-клієнта."""
    global _grpc_client_instrumented
    if not _grpc_client_instrumented:
        GrpcInstrumentorClient().instrument()
        _grpc_client_instrumented = True
