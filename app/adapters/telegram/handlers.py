import json
import logging

from app.adapters.telegram.message_handlers import private_handler
from app.adapters.telegram.message_handlers import group_handler
from app.adapters.telegram.message_handler import TelegramMessageAdapter
from app.core.dispatcher import Dispatcher

logger = logging.getLogger(__name__)


async def new_message_handler(event, client, dispatcher: Dispatcher) -> None:
    messageadapter = await TelegramMessageAdapter.from_event(event)
    if messageadapter.is_self:
        return
    if event.is_private:
        await private_handler.handle_private_message(messageadapter, dispatcher)
    elif event.is_group:
        await group_handler.handle_group_message(messageadapter, client, dispatcher)
    elif event.is_channel:
        await group_handler.handle_group_message(messageadapter, client, dispatcher)
    else:
        logger.warning(
            f"event消息: \n{json.dumps(event.message.__dict__, default=str, ensure_ascii=False)}"
        )
        logger.warning("未知消息类型，无法处理: %s", event.text)
