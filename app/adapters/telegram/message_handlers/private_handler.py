import asyncio
import logging
import random

from app.adapters.telegram.message_handler import TelegramMessageAdapter
from app.adapters.telegram.message_handlers.alert_event import ALERT_MANAGER
from app.adapters.telegram.message_handlers.audio_handler import AUDIO_HANDLER
from app.application.use_cases.screenshot import ScreenshotUseCase
from app.core.dispatcher import Dispatcher
from app.config.settings import Settings
from app.adapters.telegram.message_handlers.sensitive_word import (
    contains_sensitive_word,
)

setting = Settings()
SCREENSHOT_USE_CASE = ScreenshotUseCase()
logger = logging.getLogger(__name__)


async def handle_private_message(event: TelegramMessageAdapter, dispatcher: Dispatcher) -> None:
    logger.info(
        "私聊消息: %s | 发送者: %s | 内容: %s",
        event.chat_name,
        event.user_name,
        event.text,
    )

    # 敏感词检测
    if contains_sensitive_word(event.text, setting.sensitive_words_private):
        logger.info("检测到敏感词，播放告警音效")
        if setting.auto_screenshot_switch:
            # 播放告警音效
            AUDIO_HANDLER.play_audio(volume=0.5, loop=1)
            logger.info("自动截图开关已开启，先标记为已读，再执行截图")
            await SCREENSHOT_USE_CASE.execute(event)
        else:
            # 播放告警音乐
            AUDIO_HANDLER.play_audio(sound_file=setting.alert_sound_file, volume=0.5, loop=1)
        return

    if event.command:
        await handle_private_command(dispatcher, event)

    # 私聊告警任务
    if setting.private_alert_switch and not event.is_self:
        ALERT_MANAGER.trigger_alert(event)


async def handle_private_command(dispatcher: Dispatcher, event: TelegramMessageAdapter) -> None:
    if dispatcher:
        handler = dispatcher.router.resolve(event.command)
        if handler:
            await handler(event)
            return
        else:
            logger.info("未找到命令处理器: %s", event.command)
