import io
import json
import logging

from opentelemetry import metrics, trace
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import InMemoryMetricReader
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)

from observability.metrics import (
    record_expense_created,
    record_grpc_validation,
    record_user_auth_event,
)
from observability.telemetry import JsonLogFormatter, OTelTraceContextFilter


def test_json_logging_correlates_trace_and_span_ids():
    """Перевіряє підставлення trace_id та span_id у JSON-логи з OTel контексту."""
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.addFilter(OTelTraceContextFilter())
    handler.setFormatter(JsonLogFormatter("test-service"))

    test_logger = logging.getLogger("observability.test.logger")
    test_logger.handlers.clear()
    test_logger.addHandler(handler)
    test_logger.setLevel(logging.INFO)
    test_logger.propagate = False

    # 1. Логування поза активним Span -> trace_id та span_id мають бути "0"
    test_logger.info("Message outside span")
    outside_entry = json.loads(stream.getvalue().strip().splitlines()[-1])
    assert outside_entry["service"] == "test-service"
    assert outside_entry["message"] == "Message outside span"
    assert outside_entry["trace_id"] == "0"
    assert outside_entry["span_id"] == "0"

    # 2. Логування всередині активного Span -> реальні 32- та 16-символьні hex ID
    tracer = trace.get_tracer("test.tracer")
    with tracer.start_as_current_span("test-operation") as span:
        ctx = span.get_span_context()
        test_logger.info("Message inside active span")

    inside_entry = json.loads(stream.getvalue().strip().splitlines()[-1])
    assert inside_entry["trace_id"] == f"{ctx.trace_id:032x}"
    assert inside_entry["span_id"] == f"{ctx.span_id:016x}"
    assert inside_entry["trace_id"] != "0"
    assert inside_entry["span_id"] != "0"


def test_w3c_trace_context_propagation_across_grpc(expense_client, auth_users):
    """Перевіряє наскрізну передачу W3C Trace Context при виклику Expense - User gRPC"""
    provider = trace.get_tracer_provider()
    assert isinstance(provider, TracerProvider)

    exporter = InMemorySpanExporter()
    processor = SimpleSpanProcessor(exporter)
    provider.add_span_processor(processor)

    try:
        u1_headers = auth_users["user1"]["headers"]
        res = expense_client.post(
            "/account",
            headers=u1_headers,
            json={"balance": 200.0},
        )
        assert res.status_code == 201

        spans = exporter.get_finished_spans()
        grpc_spans = [
            s for s in spans if "/auth.AuthService/ValidateUser" in s.name
        ]
        assert len(grpc_spans) >= 1

        target_trace_id = grpc_spans[-1].context.trace_id
        same_trace_spans = [
            s for s in spans if s.context.trace_id == target_trace_id
        ]
        # В одному дереві трасування мають бути і HTTP Span, і gRPC Spans
        assert len(same_trace_spans) >= 2
    finally:
        exporter.clear()
        processor.shutdown()


def test_custom_otel_metrics_counters_and_histograms():
    """Перевіряє запис кастомних Counter та Histogram метрик у OpenTelemetry SDK."""
    reader = InMemoryMetricReader()
    provider = MeterProvider(metric_readers=[reader])
    metrics.set_meter_provider(provider)

    record_expense_created(150.0, channel="json_rpc")
    record_grpc_validation("success", 14.2)
    record_user_auth_event("login_success")

    metrics_data = reader.get_metrics_data()
    assert metrics_data is not None

    collected_names: set[str] = set()
    for resource_metrics in metrics_data.resource_metrics:
        for scope_metrics in resource_metrics.scope_metrics:
            for metric in scope_metrics.metrics:
                collected_names.add(metric.name)

    expected_metrics = {
        "expenses_created",
        "expense_amount",
        "expense_amount_distribution",
        "grpc_user_validations",
        "grpc_validation_duration_ms",
        "user_auth_events",
    }
    assert expected_metrics.issubset(collected_names)
