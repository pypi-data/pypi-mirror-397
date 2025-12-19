"""Trace class for capturing application traces."""

import secrets
import threading
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from artanis.transport import Transport


def generate_trace_id() -> str:
    """Generate a unique trace ID."""
    return f"trace_{secrets.token_urlsafe(16)}"


class Trace:
    """
    Represents a single trace of an operation.

    Traces capture inputs, outputs, and state from AI application operations.
    All methods are thread-safe and can be called multiple times.
    """

    def __init__(
        self,
        name: str,
        transport: "Transport",
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a new trace.

        Args:
            name: Name of the operation being traced
            transport: Transport instance for sending data
            metadata: Optional metadata for filtering/searching
        """
        self.id = generate_trace_id()
        self._name = name
        self._transport = transport
        self._metadata = metadata or {}

        # Trace data (thread-safe with lock)
        self._lock = threading.Lock()
        self._inputs: Dict[str, Any] = {}
        self._output: Optional[Any] = None
        self._state: Dict[str, Any] = {}
        self._error: Optional[str] = None

        # Timing
        self._start_time = time.perf_counter()
        self._timestamp = datetime.now(timezone.utc).isoformat()

        # Track if trace has been sent
        self._sent = False

    def input(self, **kwargs: Any) -> "Trace":
        """
        Record input data for this trace.

        Can be called multiple times - all inputs are merged together.

        Args:
            **kwargs: Input data as keyword arguments

        Returns:
            self (for method chaining)

        Example:
            trace.input(question="What is AI?", model="gpt-4")
            trace.input(temperature=0.7)  # Adds to existing inputs
        """
        with self._lock:
            self._inputs.update(kwargs)
        return self

    def output(self, value: Any) -> "Trace":
        """
        Record the output/result of this operation.

        Typically called once at the end. If called multiple times,
        the last value is kept.

        Args:
            value: The output value (any JSON-serializable type)

        Returns:
            self (for method chaining)

        Example:
            trace.output("AI stands for Artificial Intelligence")
            trace.output({"answer": "...", "confidence": 0.95})
        """
        with self._lock:
            self._output = value

        # Automatically send trace when output is recorded
        self._send()
        return self

    def state(self, name: str, value: Any) -> "Trace":
        """
        Capture state for replay purposes.

        State represents context needed to exactly reproduce this operation,
        such as retrieved documents, configuration, or guidelines.

        Args:
            name: Name of the state (e.g., "documents", "config", "chunks")
            value: State value (any JSON-serializable type)

        Returns:
            self (for method chaining)

        Example:
            trace.state("config", {"model": "gpt-4", "temperature": 0.7})
            trace.state("documents", [{"id": "doc1", "score": 0.95}])
        """
        with self._lock:
            self._state[name] = value
        return self

    def error(self, message: str) -> "Trace":
        """
        Record an error that occurred during this operation.

        Args:
            message: Error message or description

        Returns:
            self (for method chaining)

        Example:
            try:
                result = risky_operation()
                trace.output(result)
            except Exception as e:
                trace.error(str(e))
                raise
        """
        with self._lock:
            self._error = message

        # Send trace even on error
        self._send()
        return self

    def _send(self) -> None:
        """
        Send trace data to backend.

        This is called automatically when output() or error() is called.
        Sends data asynchronously in a fire-and-forget manner.
        """
        # Only send once
        if self._sent:
            return

        with self._lock:
            if self._sent:
                return
            self._sent = True

            # Calculate duration
            duration_ms = int((time.perf_counter() - self._start_time) * 1000)

            # Build payload
            payload = {
                "trace_id": self.id,
                "name": self._name,
                "metadata": self._metadata if self._metadata else None,
                "inputs": self._inputs,
                "output": self._output,
                "state": self._state if self._state else None,
                "timestamp": self._timestamp,
                "duration_ms": duration_ms,
            }

            # Include error if present
            if self._error:
                payload["error"] = self._error

        # Send asynchronously (fire-and-forget)
        self._transport.send("/v1/traces", payload)

    def __enter__(self) -> "Trace":
        """Support context manager usage."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """
        Automatically send trace on context exit.

        If an exception occurred, record it as an error.
        """
        if exc_val is not None:
            self.error(str(exc_val))
        elif not self._sent:
            # Send trace even if output() wasn't called
            self._send()
