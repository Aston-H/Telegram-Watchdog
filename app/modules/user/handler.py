import os
import logging

from app.adapters.telegram.message_handler import TelegramMessageAdapter
from app.application.use_cases.start import StartUseCase
from app.application.use_cases.help import HelpUseCase
from app.application.use_cases.screenshot import ScreenshotUseCase
from app.application.use_cases.req import ReqUseCase
from app.application.use_cases.blockchain import BlockchainUseCase

logger = logging.getLogger(__name__)


class UserCommandHandler:
    def __init__(self) -> None:
        self._start_use_case = StartUseCase()
        self._help_use_case = HelpUseCase()
        self._screenshot_use_case = ScreenshotUseCase()
        self._req_use_case = ReqUseCase()
        self._blockchain_use_case = BlockchainUseCase()

    async def handle_start(self, event: TelegramMessageAdapter) -> None:
        text = self._start_use_case.execute()
        await event.respond(text)

    async def handle_help(self, event: TelegramMessageAdapter) -> None:
        text = self._help_use_case.execute()
        await event.respond(text)

    async def handle_screenshot(self, event: TelegramMessageAdapter) -> None:
        image_path = None
        try:
            image_path = await self._screenshot_use_case.execute(event)
            await event.respond(file=image_path)
        except Exception as e:
            logger.error(f"截图失败：{e}")
        finally:
            if image_path and os.path.exists(image_path):
                os.remove(image_path)

    async def handle_req(self, event: TelegramMessageAdapter) -> None:
        result = await self._req_use_case.execute(event.args)
        await event.respond(result)

    async def handle_blockchain(self, event: TelegramMessageAdapter) -> None:
        result = await self._blockchain_use_case.execute(event.args)
        await event.respond(str(result))
