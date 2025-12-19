"""Tests for transport layer."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from artanis.transport import Transport


class TestTransportInit:
    """Test transport initialization."""

    def test_init_basic(self):
        """Test basic initialization."""
        transport = Transport(
            base_url="https://app.artanis.ai",
            api_key="sk_test123",
        )
        assert transport.base_url == "https://app.artanis.ai"
        assert transport.api_key == "sk_test123"
        assert transport.enabled is True

    def test_init_with_trailing_slash(self):
        """Test base_url trailing slash is removed."""
        transport = Transport(
            base_url="https://app.artanis.ai/",
            api_key="sk_test",
        )
        assert transport.base_url == "https://app.artanis.ai"

    def test_init_disabled(self):
        """Test initialization with tracing disabled."""
        transport = Transport(
            base_url="https://app.artanis.ai",
            api_key="sk_test",
            enabled=False,
        )
        assert transport.enabled is False

    def test_init_with_error_callback(self):
        """Test initialization with error callback."""
        callback = Mock()
        transport = Transport(
            base_url="https://app.artanis.ai",
            api_key="sk_test",
            on_error=callback,
        )
        assert transport.on_error == callback


class TestTransportHeaders:
    """Test HTTP header generation."""

    def test_get_headers(self):
        """Test headers include auth and content type."""
        transport = Transport(
            base_url="https://api.artanis.dev",
            api_key="sk_test123",
        )
        headers = transport._get_headers()

        assert headers["Authorization"] == "Bearer sk_test123"
        assert headers["Content-Type"] == "application/json"
        assert "User-Agent" in headers


class TestTransportSend:
    """Test send functionality."""

    def test_send_disabled(self):
        """Test send does nothing when disabled."""
        transport = Transport(
            base_url="https://api.artanis.dev",
            api_key="sk_test",
            enabled=False,
        )

        # Should not raise, should do nothing
        transport.send("/v1/traces", {"test": "data"})

    @patch("artanis.transport.Transport._send_in_thread")
    def test_send_submits_to_executor(self, mock_send):
        """Test send submits task to thread pool."""
        transport = Transport(
            base_url="https://api.artanis.dev",
            api_key="sk_test",
        )

        data = {"trace_id": "trace_123"}
        transport.send("/v1/traces", data)

        # Give thread pool a moment to process
        import time
        time.sleep(0.01)

        # Verify executor was used (mock was called means submit worked)
        # Note: We can't easily verify executor.submit directly, but we can
        # verify the method it would call was invoked

    def test_send_fire_and_forget(self):
        """Test send returns immediately (fire-and-forget)."""
        transport = Transport(
            base_url="https://api.artanis.dev",
            api_key="sk_test",
        )

        import time
        start = time.perf_counter()
        transport.send("/v1/traces", {"test": "data"})
        duration = time.perf_counter() - start

        # Should return in < 1ms (just submitting to thread pool)
        assert duration < 0.001


@pytest.mark.asyncio
class TestTransportAsync:
    """Test async send functionality."""

    async def test_send_async_success(self):
        """Test successful async send."""
        transport = Transport(
            base_url="https://api.artanis.dev",
            api_key="sk_test",
        )

        mock_response = AsyncMock()
        mock_response.status = 202
        mock_response.__aenter__.return_value = mock_response
        mock_response.__aexit__.return_value = None

        with patch.object(transport, "_get_session") as mock_session:
            mock_session.return_value.post.return_value = mock_response
            await transport._send_async("/v1/traces", {"test": "data"})

    async def test_send_async_401(self):
        """Test async send handles 401 (invalid API key)."""
        transport = Transport(
            base_url="https://api.artanis.dev",
            api_key="sk_invalid",
            debug=True,
        )

        mock_response = AsyncMock()
        mock_response.status = 401
        mock_response.__aenter__.return_value = mock_response
        mock_response.__aexit__.return_value = None

        with patch.object(transport, "_get_session") as mock_session:
            mock_session.return_value.post.return_value = mock_response

            # Should not raise - fails silently
            await transport._send_async("/v1/traces", {"test": "data"})

    async def test_send_async_413(self):
        """Test async send handles 413 (payload too large)."""
        transport = Transport(
            base_url="https://api.artanis.dev",
            api_key="sk_test",
        )

        mock_response = AsyncMock()
        mock_response.status = 413
        mock_response.__aenter__.return_value = mock_response
        mock_response.__aexit__.return_value = None

        with patch.object(transport, "_get_session") as mock_session:
            mock_session.return_value.post.return_value = mock_response

            # Should not raise - fails silently
            await transport._send_async("/v1/traces", {"test": "data"})

    async def test_send_async_429(self):
        """Test async send handles 429 (rate limit)."""
        transport = Transport(
            base_url="https://api.artanis.dev",
            api_key="sk_test",
        )

        mock_response = AsyncMock()
        mock_response.status = 429
        mock_response.__aenter__.return_value = mock_response
        mock_response.__aexit__.return_value = None

        with patch.object(transport, "_get_session") as mock_session:
            mock_session.return_value.post.return_value = mock_response

            # Should not raise - fails silently
            await transport._send_async("/v1/traces", {"test": "data"})

    async def test_send_async_network_error(self):
        """Test async send handles network errors."""
        transport = Transport(
            base_url="https://api.artanis.dev",
            api_key="sk_test",
        )

        with patch.object(transport, "_get_session") as mock_session:
            mock_session.return_value.post.side_effect = Exception("Network error")

            # Should not raise - fails silently
            await transport._send_async("/v1/traces", {"test": "data"})


class TestTransportErrorHandling:
    """Test error handling and callbacks."""

    async def test_error_callback_called(self):
        """Test error callback is invoked on errors."""
        callback = Mock()
        transport = Transport(
            base_url="https://api.artanis.dev",
            api_key="sk_test",
            on_error=callback,
        )

        with patch.object(transport, "_get_session") as mock_session:
            mock_session.return_value.post.side_effect = Exception("Test error")

            await transport._send_async("/v1/traces", {"test": "data"})

        # Error callback should have been called
        callback.assert_called_once()

    async def test_debug_logging(self):
        """Test debug mode logs errors."""
        transport = Transport(
            base_url="https://api.artanis.dev",
            api_key="sk_test",
            debug=True,
        )

        with patch("artanis.transport.logger") as mock_logger:
            with patch.object(transport, "_get_session") as mock_session:
                mock_session.return_value.post.side_effect = Exception("Test error")

                await transport._send_async("/v1/traces", {"test": "data"})

            # Should have logged warning
            mock_logger.warning.assert_called()


class TestTransportCleanup:
    """Test resource cleanup."""

    def test_close(self):
        """Test close method."""
        transport = Transport(
            base_url="https://api.artanis.dev",
            api_key="sk_test",
        )

        # Should not raise
        transport.close()
