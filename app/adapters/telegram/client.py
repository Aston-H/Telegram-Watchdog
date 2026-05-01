import logging

from telethon import TelegramClient

logger = logging.getLogger(__name__)


class TelegramClientWrapper:
    def __init__(self, api_id: int, api_hash: str, session_name: str) -> None:
        self._session_name = session_name
        self._api_id = api_id
        self._api_hash = api_hash
        self._client = TelegramClient(self._session_name, self._api_id, self._api_hash)

    def start(self) -> None:
        logger.info("启动 Telegram 客户端会话 '%s'...", self._session_name)
        self._client.start()
        logger.info("Telegram客户端已成功启动。")

    def get_client(self) -> TelegramClient:
        """获取底层的 TelegramClient 实例"""
        return self._client
