from opentelemetry import metrics

_meter = metrics.get_meter("expense-tracker.observability", version="1.0.0")

_expenses_created_counter = _meter.create_counter(
    name="expenses_created",
    description="Total number of expense records created",
)

_expense_amount_counter = _meter.create_counter(
    name="expense_amount",
    description="Total monetary volume of created expenses",
)

_expense_amount_histogram = _meter.create_histogram(
    name="expense_amount_distribution",
    description="Distribution of individual expense record amounts",
)

_grpc_validations_counter = _meter.create_counter(
    name="grpc_user_validations",
    description="Total number of gRPC ValidateUser calls",
)

_grpc_duration_histogram = _meter.create_histogram(
    name="grpc_validation_duration_ms",
    description="Latency of gRPC ValidateUser calls in milliseconds",
)

_user_auth_counter = _meter.create_counter(
    name="user_auth_events",
    description="Total user registration and login events",
)


def record_expense_created(amount: float, channel: str) -> None:
    """Фіксує створення витрати у Counter та Histogram метриках."""
    attrs = {"channel": channel}
    _expenses_created_counter.add(1, attributes=attrs)
    _expense_amount_counter.add(amount, attributes=attrs)
    _expense_amount_histogram.record(amount, attributes=attrs)


def record_grpc_validation(status: str, duration_ms: float) -> None:
    """Фіксує результат та час виконання міжсервісного gRPC-виклику."""
    attrs = {"status": status}
    _grpc_validations_counter.add(1, attributes=attrs)
    _grpc_duration_histogram.record(duration_ms, attributes=attrs)


def record_user_auth_event(event: str) -> None:
    """Фіксує події реєстрації та аутентифікації у User Service."""
    _user_auth_counter.add(1, attributes={"event": event})
