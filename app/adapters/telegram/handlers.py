import json
import logging

from app.adapters.telegram.message_handlers import private_handler
from app.adapters.telegram.message_handlers import group_handler
from app.adapters.telegram.message_handler import TelegramMessageAdapter
from app.config.settings import Settings
from app.core.dispatcher import Dispatcher

logger = logging.getLogger(__name__)
setting = Settings()


async def new_message_handler(event, client, dispatcher: Dispatcher) -> None:
    # 将事件转换为消息适配器
    messageadapter = await TelegramMessageAdapter.from_event(event)
    # 过滤指定群组
    if messageadapter.chat_id and messageadapter.chat_id in setting.filtered_chat_ids:
        return
    # 根据消息类型调用不同的处理器
    if event.is_private:
        await private_handler.handle_private_message(messageadapter, dispatcher)
    elif event.is_group:
        await group_handler.handle_group_message(messageadapter, client, dispatcher)
    elif event.is_channel:
        await group_handler.handle_group_message(messageadapter, client, dispatcher)
    else:
        logger.info(f"event消息: \n{json.dumps(event.message.__dict__, default=str, ensure_ascii=False)}")
        logger.warning("未知消息类型，无法处理: %s", event.text)
