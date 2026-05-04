from __future__ import annotations

import asyncio
import logging
import os
import random
import shutil
import subprocess
import tempfile
from typing import Optional
from app.adapters.telegram.message_handler import TelegramMessageAdapter

logger = logging.getLogger(__name__)


class ScreenshotUseCase:
    """截图用例"""

    async def execute(self, event: TelegramMessageAdapter = None) -> str:
        try:
            if event:
                delay = random.randint(10, 20)
                logger.info(f"模拟真实行为，等待 {delay * 2} 秒后再截图...")
                await asyncio.sleep(delay)
                await event.mark_as_read()
            await asyncio.sleep(delay)

            offset = random.randint(5, 10)
            if event.args:
                parts = [p.strip() for p in event.args.split(",")]
                x, y, w, h = int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3])
            else:
                x, y, w, h = 1450, 1, 400, 60

            x += random.choice([-1, 1]) * offset * 3
            y += random.choice([-1, 1]) * offset
            w += random.choice([-1, 1]) * offset
            h += random.choice([-1, 1]) * offset * 2

            region = f"{x},{y},{w},{h}"
            image_path = await self.capture(region=region)
            if not await event.is_message_exists():
                logger.info("消息已不存在，跳过发送截图")
                return
            await event.respond(file=image_path)
            logger.info("截图已发送: %s", image_path)
        except ValueError as error:
            logger.info(f"参数错误：{error}")
        except RuntimeError as error:
            logger.info(f"截图失败：{error}")
        except Exception as e:
            logger.error("截图失败: %s", e)

    async def capture(self, region: Optional[str] = None) -> str:
        if shutil.which("screencapture") is None:
            raise RuntimeError("当前环境不支持截图，找不到 screencapture 工具")

        image_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        image_file.close()
        path = image_file.name

        command = ["screencapture", "-x"]
        if region:
            command += ["-R", self._normalize_region(region)]
        command.append(path)

        result = subprocess.run(command, capture_output=True)
        if result.returncode != 0:
            os.remove(path)
            raise RuntimeError(
                result.stderr.decode(errors="ignore").strip() or "未知错误"
            )

        if not os.path.exists(path) or os.path.getsize(path) == 0:
            raise RuntimeError("截图未生成")

        return path

    def _normalize_region(self, region: str) -> str:
        parts = [part.strip() for part in region.split(",")]
        if len(parts) != 4:
            raise ValueError("区域参数格式错误，请使用 x,y,w,h")

        try:
            x, y, width, height = (int(part) for part in parts)
        except ValueError:
            raise ValueError("区域参数必须为整数：x,y,w,h")

        if width <= 0 or height <= 0:
            raise ValueError("宽度和高度必须大于 0")

        return f"{x},{y},{width},{height}"
