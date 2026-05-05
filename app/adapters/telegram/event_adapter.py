from telethon import events
import logging
import time

from app.adapters.telegram.client import TelegramClientWrapper
from app.adapters.telegram.handlers import new_message_handler
from app.adapters.telegram.message_handlers.audio_handler import AudioHandler
from app.config.settings import Settings

logger = logging.getLogger(__name__)
setting = Settings()
AUDIO_HANDLER = AudioHandler()


class TelegramEventAdapter:
    def __init__(self, client_wrapper: TelegramClientWrapper, dispatcher) -> None:
        self._client_wrapper = client_wrapper
        self._dispatcher = dispatcher
        self._client = client_wrapper.get_client()
        self._running = True

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
        while self._running:
            try:
                logger.info("正在连接 Telegram...")
                self._client_wrapper.start()
                logger.info("连接成功，开始监听消息...")
                self._client.run_until_disconnected()
            except (ConnectionError, OSError) as e:
                logger.warning(f"连接断开: {e}, 10秒后重试...")
                AUDIO_HANDLER.play_audio(sound_file=setting.alert_sound_file, volume=0.2, loop=1)
                time.sleep(10)
            except KeyboardInterrupt:
                logger.info("收到中断信号，停止运行")
                self._running = False
                break
            except Exception as e:
                logger.error(f"发生异常: {e}, 10秒后重试...")
                time.sleep(10)
