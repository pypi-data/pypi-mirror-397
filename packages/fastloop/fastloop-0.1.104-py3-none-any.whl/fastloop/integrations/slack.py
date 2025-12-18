from collections.abc import Awaitable, Callable
from http import HTTPStatus
from typing import TYPE_CHECKING, Any, cast

from fastapi import HTTPException, Request
from slack_sdk.signature import SignatureVerifier
from slack_sdk.web.async_client import AsyncWebClient

from ..integrations import Integration
from ..models import LoopEvent, LoopState
from ..types import IntegrationType

if TYPE_CHECKING:
    from ..context import LoopContext
    from ..fastloop import FastLoop

SlackSetupCallback = Callable[["LoopContext", "LoopEvent"], Awaitable[str]]


class SlackMessageEvent(LoopEvent):
    type: str = "slack_message"
    channel: str
    user: str
    text: str
    ts: str
    thread_ts: str | None = None
    team: str
    event_ts: str


class SlackReactionEvent(LoopEvent):
    type: str = "slack_reaction"
    channel: str
    user: str
    reaction: str
    item_user: str
    item: dict[str, Any] | None = None
    event_ts: str


class SlackAppMentionEvent(LoopEvent):
    type: str = "slack_app_mention"
    channel: str
    user: str
    text: str
    ts: str
    thread_ts: str | None = None
    team: str
    event_ts: str


class SlackFileSharedEvent(LoopEvent):
    type: str = "slack_file_shared"
    file_id: str
    user: str
    channel: str
    event_ts: str

    async def download_file(self, context: "LoopContext") -> bytes:
        from aiohttp import ClientSession

        integration = context.integrations.get(IntegrationType.SLACK)
        if integration is None:
            raise ValueError("Slack integration not found in context")

        client = integration.get_client_for_context(context)
        file_info = await client.files_info(file=self.file_id)
        file_obj = file_info.get("file", {})
        download_url = file_obj.get("url_private_download") or file_obj.get(
            "url_private"
        )

        if not download_url:
            raise ValueError(f"No download URL found for file {self.file_id}")

        headers = {"Authorization": f"Bearer {client.token}"}
        async with (
            ClientSession() as session,
            session.get(download_url, headers=headers) as resp,
        ):
            resp.raise_for_status()
            return await resp.read()


SUPPORTED_SLACK_EVENTS = [
    "message",
    "app_mention",
    "reaction_added",
    "file_shared",
]


class SlackIntegration(Integration):
    def __init__(
        self,
        *,
        signing_secret: str,
        setup: SlackSetupCallback,
    ):
        super().__init__()
        self._setup_callback = setup
        self._signing_secret = signing_secret
        self.verifier = SignatureVerifier(signing_secret)

    def type(self) -> IntegrationType:
        return IntegrationType.SLACK

    async def setup_for_context(
        self, context: "LoopContext", event: "LoopEvent"
    ) -> AsyncWebClient:
        bot_token = await self._setup_callback(context, event)
        client = AsyncWebClient(token=bot_token)
        context.set_integration_client(self.type(), client)
        return client

    def get_client_for_context(self, context: "LoopContext") -> AsyncWebClient:
        client = context.get_integration_client(self.type())
        if client is None:
            raise ValueError(
                "Slack client not initialized for this context. "
                "Ensure setup_for_context was called."
            )
        return cast("AsyncWebClient", client)

    def register(self, fastloop: "FastLoop", loop_name: str) -> None:
        fastloop.register_events(
            [
                SlackMessageEvent,
                SlackAppMentionEvent,
                SlackReactionEvent,
                SlackFileSharedEvent,
            ]
        )

        self._fastloop: FastLoop = fastloop
        self._fastloop.add_api_route(
            path=f"/{loop_name}/slack/events",
            endpoint=self._handle_slack_event,
            methods=["POST"],
            response_model=None,
        )
        self.loop_name: str = loop_name

    def _ok(self) -> dict[str, Any]:
        return {"ok": True}

    async def _handle_slack_event(self, request: Request):
        body = await request.body()

        if not self.verifier.is_valid_request(body, dict(request.headers)):
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN, detail="Invalid signature"
            )

        payload = await request.json()
        if payload.get("type") == "url_verification":
            return {"challenge": payload["challenge"]}

        event: dict[str, str] = payload.get("event", {})
        event_type = event.get("type")

        if event_type not in SUPPORTED_SLACK_EVENTS:
            return self._ok()

        if event_type.startswith("file_"):
            event = await self._lookup_file_info(event)

        thread_ts = event.get("thread_ts") or event.get("ts") or ""
        channel: str = event.get("channel", "")
        user = event.get("user", "")
        text = event.get("text", "")
        team = event.get("team", "") or payload.get("team_id", "")
        event_ts = event.get("event_ts", "")
        reaction = event.get("reaction", "")
        item_user = event.get("item_user", "")
        item = cast("dict[str, Any]", event.get("item"))

        loop_id = await self._fastloop.state_manager.get_loop_mapping(
            f"slack_thread:{channel}:{thread_ts}"
        )

        loop_event_handler = self._fastloop.loop_event_handlers.get(self.loop_name)
        if not loop_event_handler:
            return self._ok()

        loop_event: LoopEvent | None = None
        if event_type == "app_mention":
            loop_event = SlackAppMentionEvent(
                loop_id=loop_id or None,
                channel=channel,
                user=user,
                text=text,
                ts=thread_ts,
                team=team,
                event_ts=event_ts,
            )
        elif event_type == "message":
            loop_event = SlackMessageEvent(
                loop_id=loop_id or None,
                channel=channel,
                user=user,
                text=text,
                ts=thread_ts,
                team=team,
                event_ts=event_ts,
            )
        elif event_type == "reaction_added":
            loop_event = SlackReactionEvent(
                loop_id=loop_id or None,
                channel=channel,
                user=user,
                reaction=reaction,
                item_user=item_user,
                item=item,
                event_ts=event_ts,
            )
        elif event_type == "file_shared":
            loop_event = SlackFileSharedEvent(
                loop_id=loop_id or None,
                file_id=event.get("file_id", ""),
                user=user,
                channel=channel,
                event_ts=event_ts,
            )

        mapped_request: dict[str, Any] = loop_event.to_dict() if loop_event else {}
        loop: LoopState = await loop_event_handler(mapped_request)
        if loop.loop_id:
            await self._fastloop.state_manager.set_loop_mapping(
                f"slack_thread:{channel}:{thread_ts}", loop.loop_id
            )

        return self._ok()

    def events(self) -> list[Any]:
        return [
            SlackMessageEvent,
            SlackAppMentionEvent,
            SlackReactionEvent,
            SlackFileSharedEvent,
        ]

    async def _lookup_file_info(self, event: dict[str, str]) -> dict[str, str]:
        return event

    async def emit(self, event: Any, context: "LoopContext | None" = None) -> None:
        if context is None:
            raise ValueError("Context is required for Slack integration")

        client = self.get_client_for_context(context)

        if isinstance(event, SlackMessageEvent):
            await client.chat_postMessage(
                channel=event.channel, text=event.text, thread_ts=event.thread_ts
            )
        elif isinstance(event, SlackReactionEvent):
            await client.reactions_add(
                channel=event.channel,
                name=event.reaction,
                timestamp=event.event_ts,
                item_user=event.item_user,
                item=event.item,
            )
        elif isinstance(event, SlackAppMentionEvent):
            await client.chat_postMessage(
                channel=event.channel,
                text=event.text,
                thread_ts=event.thread_ts,
            )
        elif isinstance(event, SlackFileSharedEvent):
            raise NotImplementedError(
                "File sharing from inside loops is not supported yet."
            )
