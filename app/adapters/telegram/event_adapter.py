from telethon import events
import json
import logging

from app.adapters.telegram.client import TelegramClientWrapper
from app.adapters.telegram.handlers import new_message_handler
from app.adapters.telegram.message_handlers.audio_handler import AudioHandler
from app.config.settings import Settings

logger = logging.getLogger(__name__)
setting = Settings()
AUDIO_HANDLER = AudioHandler()


class NetworkAlertHandler(logging.Handler):
    """自定义日志处理器，检测网络断开并播放音效"""

    def __init__(self):
        super().__init__()
    

    def emit(self, record):
        if record.levelno >= logging.WARNING:
            msg = record.getMessage()
            if "Network is unreachable" in msg or "Can't assign requested address" in msg:
                AUDIO_HANDLER.play_audio(volume=0.8, loop=1)


# 添加自定义日志处理器
_network_handler = NetworkAlertHandler()
_network_handler.setLevel(logging.WARNING)
logging.getLogger("telethon").addHandler(_network_handler)


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
