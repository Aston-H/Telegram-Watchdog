from telethon import events
import json
import logging

from app.adapters.telegram.client import TelegramClientWrapper
from app.adapters.telegram.handlers import new_message_handler
from app.config.settings import Settings

logger = logging.getLogger(__name__)
setting = Settings()


class TelegramEventAdapter:
    def __init__(self, client_wrapper: TelegramClientWrapper, dispatcher) -> None:
        self._client_wrapper = client_wrapper
        self._dispatcher = dispatcher
        self._client = client_wrapper.get_client()

    def register_handlers(self) -> None:
        self._client.add_event_handler(
            lambda event: new_message_handler(event, self._client, self._dispatcher),
            events.NewMessage,
        )
        self._client.add_event_handler(
            lambda event: new_message_handler(event, self._client, self._dispatcher),
            events.MessageEdited,
        )

    def start(self) -> None:
        self.register_handlers()
        self._client_wrapper.start()
        self._client.run_until_disconnected()
