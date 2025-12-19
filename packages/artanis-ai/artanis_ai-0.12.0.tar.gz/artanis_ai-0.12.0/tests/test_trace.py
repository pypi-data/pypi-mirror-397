"""Tests for Trace class."""

import time
import pytest
from unittest.mock import Mock, patch

from artanis.trace import Trace, generate_trace_id


class TestTraceId:
    """Test trace ID generation."""

    def test_generate_trace_id_format(self):
        """Test trace ID has correct format."""
        trace_id = generate_trace_id()
        assert trace_id.startswith("trace_")
        assert len(trace_id) > 10

    def test_generate_trace_id_unique(self):
        """Test trace IDs are unique."""
        ids = [generate_trace_id() for _ in range(100)]
        assert len(set(ids)) == 100


class TestTraceInput:
    """Test trace input recording."""

    def test_input_single_call(self):
        """Test recording inputs in single call."""
        transport = Mock()
        trace = Trace("test-op", transport)
        trace.input(question="What is AI?", model="gpt-4")

        assert trace._inputs["question"] == "What is AI?"
        assert trace._inputs["model"] == "gpt-4"

    def test_input_multiple_calls(self):
        """Test inputs from multiple calls are merged."""
        transport = Mock()
        trace = Trace("test-op", transport)
        trace.input(question="What is AI?")
        trace.input(model="gpt-4")
        trace.input(temperature=0.7)

        assert trace._inputs["question"] == "What is AI?"
        assert trace._inputs["model"] == "gpt-4"
        assert trace._inputs["temperature"] == 0.7

    def test_input_returns_self(self):
        """Test input() returns self for chaining."""
        transport = Mock()
        trace = Trace("test-op", transport)
        result = trace.input(test="value")
        assert result is trace


class TestTraceOutput:
    """Test trace output recording."""

    @patch("artanis.trace.Trace._send")
    def test_output_string(self, mock_send):
        """Test recording string output."""
        transport = Mock()
        trace = Trace("test-op", transport)
        trace.output("AI stands for Artificial Intelligence")

        assert trace._output == "AI stands for Artificial Intelligence"
        mock_send.assert_called_once()

    @patch("artanis.trace.Trace._send")
    def test_output_dict(self, mock_send):
        """Test recording dict output."""
        transport = Mock()
        trace = Trace("test-op", transport)
        output = {"answer": "test", "confidence": 0.95}
        trace.output(output)

        assert trace._output == output

    @patch("artanis.trace.Trace._send")
    def test_output_triggers_send(self, mock_send):
        """Test output() triggers trace send."""
        transport = Mock()
        trace = Trace("test-op", transport)
        trace.output("result")

        mock_send.assert_called_once()

    @patch("artanis.trace.Trace._send")
    def test_output_returns_self(self, mock_send):
        """Test output() returns self for chaining."""
        transport = Mock()
        trace = Trace("test-op", transport)
        result = trace.output("test")
        assert result is trace


class TestTraceState:
    """Test trace state recording."""

    def test_state_single_entry(self):
        """Test recording single state entry."""
        transport = Mock()
        trace = Trace("test-op", transport)
        trace.state("config", {"model": "gpt-4"})

        assert trace._state["config"] == {"model": "gpt-4"}

    def test_state_multiple_entries(self):
        """Test recording multiple state entries."""
        transport = Mock()
        trace = Trace("test-op", transport)
        trace.state("config", {"model": "gpt-4"})
        trace.state("documents", [{"id": "doc1"}])
        trace.state("chunks", [{"id": "chunk1"}])

        assert len(trace._state) == 3
        assert trace._state["config"] == {"model": "gpt-4"}
        assert trace._state["documents"] == [{"id": "doc1"}]

    def test_state_returns_self(self):
        """Test state() returns self for chaining."""
        transport = Mock()
        trace = Trace("test-op", transport)
        result = trace.state("test", "value")
        assert result is trace


class TestTraceError:
    """Test trace error recording."""

    @patch("artanis.trace.Trace._send")
    def test_error_recording(self, mock_send):
        """Test recording error."""
        transport = Mock()
        trace = Trace("test-op", transport)
        trace.error("Something went wrong")

        assert trace._error == "Something went wrong"
        mock_send.assert_called_once()

    @patch("artanis.trace.Trace._send")
    def test_error_triggers_send(self, mock_send):
        """Test error() triggers trace send."""
        transport = Mock()
        trace = Trace("test-op", transport)
        trace.error("Error message")

        mock_send.assert_called_once()


class TestTraceSend:
    """Test trace sending."""

    def test_send_payload_structure(self):
        """Test send creates correct payload structure."""
        transport = Mock()
        trace = Trace("test-op", transport, metadata={"user_id": "user-123"})
        trace.input(question="What is AI?")
        trace.state("config", {"model": "gpt-4"})
        trace.output("AI stands for Artificial Intelligence")

        # Check transport.send was called
        transport.send.assert_called_once()

        # Verify payload structure
        call_args = transport.send.call_args[0]
        endpoint = call_args[0]
        payload = call_args[1]

        assert endpoint == "/v1/traces"
        assert payload["trace_id"] == trace.id
        assert payload["name"] == "test-op"
        assert payload["metadata"] == {"user_id": "user-123"}
        assert payload["inputs"] == {"question": "What is AI?"}
        assert payload["output"] == "AI stands for Artificial Intelligence"
        assert payload["state"] == {"config": {"model": "gpt-4"}}
        assert "timestamp" in payload
        assert "duration_ms" in payload

    def test_send_only_once(self):
        """Test trace is only sent once."""
        transport = Mock()
        trace = Trace("test-op", transport)
        trace.output("result 1")
        trace.output("result 2")

        # Should only send once despite multiple output calls
        transport.send.assert_called_once()

    def test_send_with_error(self):
        """Test send includes error if present."""
        transport = Mock()
        trace = Trace("test-op", transport)
        trace.error("Test error")

        call_args = transport.send.call_args[0]
        payload = call_args[1]
        assert payload["error"] == "Test error"

    def test_duration_calculation(self):
        """Test duration is calculated correctly."""
        transport = Mock()
        trace = Trace("test-op", transport)

        # Simulate some work
        time.sleep(0.01)  # 10ms

        trace.output("result")

        call_args = transport.send.call_args[0]
        payload = call_args[1]

        # Duration should be >= 10ms (allowing for timing variance)
        assert payload["duration_ms"] >= 8


class TestTraceContextManager:
    """Test trace context manager support."""

    @patch("artanis.trace.Trace._send")
    def test_context_manager(self, mock_send):
        """Test trace can be used as context manager."""
        transport = Mock()
        with Trace("test-op", transport) as trace:
            trace.input(data="test")
            trace.output("result")

        # Should send on exit
        mock_send.assert_called()

    def test_context_manager_with_exception(self):
        """Test context manager records exception as error."""
        transport = Mock()

        with pytest.raises(ValueError):
            with Trace("test-op", transport) as trace:
                trace.input(data="test")
                raise ValueError("Test error")

        # Should record error and send
        transport.send.assert_called_once()
        call_args = transport.send.call_args[0]
        payload = call_args[1]
        assert payload["error"] == "Test error"

    @patch("artanis.trace.Trace._send")
    def test_context_manager_auto_send(self, mock_send):
        """Test context manager auto-sends even without output()."""
        transport = Mock()

        with Trace("test-op", transport) as trace:
            trace.input(data="test")
            # No output() call

        # Should still send on exit
        mock_send.assert_called_once()


class TestTraceChaining:
    """Test method chaining."""

    @patch("artanis.trace.Trace._send")
    def test_method_chaining(self, mock_send):
        """Test methods can be chained."""
        transport = Mock()
        trace = Trace("test-op", transport)

        # Chain all methods
        result = (
            trace.input(question="What is AI?")
            .state("config", {"model": "gpt-4"})
            .output("AI stands for Artificial Intelligence")
        )

        assert result is trace
        assert trace._inputs["question"] == "What is AI?"
        assert trace._state["config"] == {"model": "gpt-4"}
        assert trace._output == "AI stands for Artificial Intelligence"
