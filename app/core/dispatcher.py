import inspect
import logging

from app.core.router import Router
from app.adapters.telegram.message_handler import TelegramMessageAdapter

logger = logging.getLogger(__name__)


class Dispatcher:
    def __init__(self, router: Router) -> None:
        self.router = router

    async def dispatch(self, event: TelegramMessageAdapter) -> None:
        handler = self.router.resolve(event.command)
        if handler is None:
            logger.debug("未识别命令或未注册路由: %s", event.text)
            return

        logger.info("调度命令 %s", event.command)
        result = handler(event)
        if inspect.isawaitable(result):
            await result
