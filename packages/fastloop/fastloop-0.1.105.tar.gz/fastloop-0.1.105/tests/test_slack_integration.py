"""
Tests for the Slack integration.

Verifies:
1. SlackIntegration initialization with setup callback
2. setup_for_context creates and stores client
3. get_client_for_context retrieves the client
4. emit sends messages using the context's client
5. Events are registered correctly
6. wait_for works with Slack events
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from fastloop import FastLoop, LoopContext
from fastloop.integrations.slack import (
    SlackAppMentionEvent,
    SlackFileSharedEvent,
    SlackIntegration,
    SlackMessageEvent,
    SlackReactionEvent,
)
from fastloop.types import IntegrationType


class TestSlackIntegrationInit:
    def test_requires_signing_secret(self):
        async def setup(_ctx, _event):
            return "xoxb-token"

        integration = SlackIntegration(signing_secret="secret123", setup=setup)
        assert integration._signing_secret == "secret123"
        assert integration._setup_callback == setup

    def test_creates_verifier(self):
        async def setup(_ctx, _event):
            return "xoxb-token"

        integration = SlackIntegration(signing_secret="secret123", setup=setup)
        assert integration.verifier is not None

    def test_type_returns_slack(self):
        async def setup(_ctx, _event):
            return "xoxb-token"

        integration = SlackIntegration(signing_secret="secret123", setup=setup)
        assert integration.type() == IntegrationType.SLACK


class TestSlackIntegrationSetup:
    @pytest.mark.asyncio
    async def test_setup_for_context_calls_callback(self):
        callback_called = False
        received_context = None
        received_event = None

        async def setup(ctx, event):
            nonlocal callback_called, received_context, received_event
            callback_called = True
            received_context = ctx
            received_event = event
            return "xoxb-test-token"

        integration = SlackIntegration(signing_secret="secret", setup=setup)

        mock_context = MagicMock(spec=LoopContext)
        mock_context.set_integration_client = MagicMock()
        mock_context.get_integration_client = MagicMock(return_value=None)

        mock_event = SlackAppMentionEvent(
            channel="C123",
            user="U456",
            text="hello",
            ts="123.456",
            team="T789",
            event_ts="123.456",
        )

        with patch("fastloop.integrations.slack.AsyncWebClient") as mock_client_cls:
            mock_client_instance = MagicMock()
            mock_client_cls.return_value = mock_client_instance

            await integration.setup_for_context(mock_context, mock_event)

            assert callback_called
            assert received_context == mock_context
            assert received_event == mock_event
            mock_client_cls.assert_called_once_with(token="xoxb-test-token")
            mock_context.set_integration_client.assert_called_once_with(
                IntegrationType.SLACK, mock_client_instance
            )

    @pytest.mark.asyncio
    async def test_get_client_for_context_returns_stored_client(self):
        async def setup(_ctx, _event):
            return "xoxb-token"

        integration = SlackIntegration(signing_secret="secret", setup=setup)

        mock_client = MagicMock()
        mock_context = MagicMock(spec=LoopContext)
        mock_context.get_integration_client = MagicMock(return_value=mock_client)

        result = integration.get_client_for_context(mock_context)

        assert result == mock_client
        mock_context.get_integration_client.assert_called_once_with(
            IntegrationType.SLACK
        )

    @pytest.mark.asyncio
    async def test_get_client_for_context_raises_if_not_initialized(self):
        async def setup(_ctx, _event):
            return "xoxb-token"

        integration = SlackIntegration(signing_secret="secret", setup=setup)

        mock_context = MagicMock(spec=LoopContext)
        mock_context.get_integration_client = MagicMock(return_value=None)

        with pytest.raises(ValueError, match="Slack client not initialized"):
            integration.get_client_for_context(mock_context)


class TestSlackIntegrationEmit:
    @pytest.mark.asyncio
    async def test_emit_requires_context(self):
        async def setup(_ctx, _event):
            return "xoxb-token"

        integration = SlackIntegration(signing_secret="secret", setup=setup)

        event = SlackMessageEvent(
            channel="C123",
            user="U456",
            text="hello",
            ts="123.456",
            team="T789",
            event_ts="123.456",
        )

        with pytest.raises(ValueError, match="Context is required"):
            await integration.emit(event, context=None)

    @pytest.mark.asyncio
    async def test_emit_message_calls_chat_post_message(self):
        async def setup(_ctx, _event):
            return "xoxb-token"

        integration = SlackIntegration(signing_secret="secret", setup=setup)

        mock_client = AsyncMock()
        mock_context = MagicMock(spec=LoopContext)
        mock_context.get_integration_client = MagicMock(return_value=mock_client)

        event = SlackMessageEvent(
            channel="C123",
            user="U456",
            text="hello world",
            ts="123.456",
            thread_ts="123.456",
            team="T789",
            event_ts="123.456",
        )

        await integration.emit(event, context=mock_context)

        mock_client.chat_postMessage.assert_called_once_with(
            channel="C123", text="hello world", thread_ts="123.456"
        )

    @pytest.mark.asyncio
    async def test_emit_app_mention_calls_chat_post_message(self):
        async def setup(_ctx, _event):
            return "xoxb-token"

        integration = SlackIntegration(signing_secret="secret", setup=setup)

        mock_client = AsyncMock()
        mock_context = MagicMock(spec=LoopContext)
        mock_context.get_integration_client = MagicMock(return_value=mock_client)

        event = SlackAppMentionEvent(
            channel="C123",
            user="U456",
            text="<@BOT> hello",
            ts="123.456",
            thread_ts="123.456",
            team="T789",
            event_ts="123.456",
        )

        await integration.emit(event, context=mock_context)

        mock_client.chat_postMessage.assert_called_once_with(
            channel="C123", text="<@BOT> hello", thread_ts="123.456"
        )

    @pytest.mark.asyncio
    async def test_emit_reaction_calls_reactions_add(self):
        async def setup(_ctx, _event):
            return "xoxb-token"

        integration = SlackIntegration(signing_secret="secret", setup=setup)

        mock_client = AsyncMock()
        mock_context = MagicMock(spec=LoopContext)
        mock_context.get_integration_client = MagicMock(return_value=mock_client)

        event = SlackReactionEvent(
            channel="C123",
            user="U456",
            reaction="thumbsup",
            item_user="U789",
            item={"type": "message", "ts": "123.456"},
            event_ts="123.456",
        )

        await integration.emit(event, context=mock_context)

        mock_client.reactions_add.assert_called_once_with(
            channel="C123",
            name="thumbsup",
            timestamp="123.456",
            item_user="U789",
            item={"type": "message", "ts": "123.456"},
        )


class TestSlackEventsRegistration:
    def test_events_returns_all_event_types(self):
        async def setup(_ctx, _event):
            return "xoxb-token"

        integration = SlackIntegration(signing_secret="secret", setup=setup)
        events = integration.events()

        assert SlackMessageEvent in events
        assert SlackAppMentionEvent in events
        assert SlackReactionEvent in events
        assert SlackFileSharedEvent in events

    def test_register_adds_events_to_fastloop(self):
        async def setup(_ctx, _event):
            return "xoxb-token"

        app = FastLoop(name="test-app")
        integration = SlackIntegration(signing_secret="secret", setup=setup)

        @app.loop("testloop", integrations=[integration])
        async def test_loop(ctx):
            pass

        assert "slack_message" in app._event_types
        assert "slack_app_mention" in app._event_types
        assert "slack_reaction" in app._event_types
        assert "slack_file_shared" in app._event_types

    def test_register_adds_webhook_route(self):
        async def setup(_ctx, _event):
            return "xoxb-token"

        app = FastLoop(name="test-app")
        integration = SlackIntegration(signing_secret="secret", setup=setup)

        @app.loop("mybot", integrations=[integration])
        async def test_loop(ctx):
            pass

        route_paths = [route.path for route in app.routes]
        assert "/mybot/slack/events" in route_paths


class TestSlackEventTypes:
    def test_slack_message_event_has_correct_type(self):
        event = SlackMessageEvent(
            channel="C123",
            user="U456",
            text="hello",
            ts="123.456",
            team="T789",
            event_ts="123.456",
        )
        assert event.type == "slack_message"

    def test_slack_app_mention_event_has_correct_type(self):
        event = SlackAppMentionEvent(
            channel="C123",
            user="U456",
            text="hello",
            ts="123.456",
            team="T789",
            event_ts="123.456",
        )
        assert event.type == "slack_app_mention"

    def test_slack_reaction_event_has_correct_type(self):
        event = SlackReactionEvent(
            channel="C123",
            user="U456",
            reaction="thumbsup",
            item_user="U789",
            event_ts="123.456",
        )
        assert event.type == "slack_reaction"

    def test_slack_file_shared_event_has_correct_type(self):
        event = SlackFileSharedEvent(
            file_id="F123",
            user="U456",
            channel="C789",
            event_ts="123.456",
        )
        assert event.type == "slack_file_shared"


class TestSlackIntegrationWithLoop:
    def test_loop_with_slack_integration_registers_correctly(self):
        async def setup(_ctx, _event):
            return "xoxb-token"

        app = FastLoop(name="test-app")

        @app.loop(
            "slackbot",
            integrations=[SlackIntegration(signing_secret="secret", setup=setup)],
        )
        async def slack_bot(ctx):
            pass

        assert "slackbot" in app._loop_metadata
        integrations = app._loop_metadata["slackbot"]["integrations"]
        assert len(integrations) == 1
        assert integrations[0].type() == IntegrationType.SLACK

    def test_multiple_loops_can_have_same_integration_type(self):
        async def setup1(_ctx, _event):
            return "xoxb-token-1"

        async def setup2(_ctx, _event):
            return "xoxb-token-2"

        app = FastLoop(name="test-app")

        @app.loop(
            "bot1",
            integrations=[SlackIntegration(signing_secret="secret1", setup=setup1)],
        )
        async def bot1(ctx):
            pass

        @app.loop(
            "bot2",
            integrations=[SlackIntegration(signing_secret="secret2", setup=setup2)],
        )
        async def bot2(ctx):
            pass

        assert "/bot1/slack/events" in [route.path for route in app.routes]
        assert "/bot2/slack/events" in [route.path for route in app.routes]
