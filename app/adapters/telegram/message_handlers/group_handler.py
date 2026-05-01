import logging
from app.adapters.telegram.message_handler import TelegramMessageAdapter
from app.adapters.telegram.message_handlers.alert_event import ALERT_MANAGER
from app.adapters.telegram.message_handlers.sensitive_word import (
    contains_sensitive_word,
)
from app.config.settings import Settings
from app.core.dispatcher import Dispatcher

setting = Settings()
logger = logging.getLogger(__name__)


async def handle_group_message(event, client, dispatcher: Dispatcher) -> None:
    logger.info(
        "群聊消息 from %s: %s: %s",
        event.sender_id,
        event.chat_id,
        event.text,
    )

    # 敏感词检测
    if contains_sensitive_word(event.text, setting.sensitive_words_group):
        logger.info("检测到敏感词，播放告警音效")
        ALERT_MANAGER.trigger_alert(event)
