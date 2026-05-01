import json
import logging

from dataclasses import dataclass
from typing import Optional
from telethon import events
from telethon.tl.custom.message import Message

logger = logging.getLogger(__name__)


@dataclass
class TelegramMessageAdapter:
    """Telegram 消息适配器"""

    raw_event: events.NewMessage
    message: Message
    text: str
    sender_id: int
    chat_id: int
    command: Optional[str] = None
    args: Optional[str] = None
    is_self: bool = False

    @classmethod
    async def from_event(cls, event) -> "TelegramMessageAdapter":
        """从 telethon event 创建适配器"""
        text = event.message.message or ""

        # 解析命令和参数
        command: bool = False
        args = None
        textstrip = text.strip()
        command, _, args = (
            textstrip.partition(" ") if textstrip.startswith("/") else (None, "", None)
        )

        return cls(
            raw_event=event,
            message=event.message,
            text=text,
            sender_id=event.sender_id,
            chat_id=event.chat_id,
            command=command,
            args=args,
            is_self=event.out,
        )

    async def reply(self, text: str = "", **kwargs) -> None:
        """回复消息"""
        await self.message.reply(text, **kwargs)

    async def respond(self, text: str = "", **kwargs) -> None:
        """发送消息（作为新消息而非回复）"""
        await self.message.respond(text, **kwargs)

    async def mark_as_read(self) -> None:
        """标记消息为已读"""
        await self.message.mark_read()

    async def is_message_exists(self) -> bool:
        """检测消息是否还存在"""
        # 检查消息对象的 deleted 属性
        if hasattr(self.message, "deleted") and self.message.deleted:
            return False

        # 如果消息对象本身为 None，则不存在
        if self.message is None:
            return False

        # 尝试重新获取消息以确认存在
        try:
            messages = await self.message.client.get_messages(
                self.chat_id, ids=self.message.id
            )
            # get_messages 返回消息对象如果存在，否则返回 None 或抛出异常
            if messages is None:
                return False
            if isinstance(messages, list):
                return len(messages) > 0 and messages[0] is not None
            return messages is not None
        except Exception:
            return False
