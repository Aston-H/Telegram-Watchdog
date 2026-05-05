import json
import logging

from dataclasses import dataclass
from typing import Optional
from telethon.tl.custom.message import Message

logger = logging.getLogger(__name__)


@dataclass
class TelegramMessageAdapter:
    """Telegram 消息适配器"""
    message: Message
    text: str
    sender_id: int
    chat_id: int
    command: Optional[str] = None
    args: Optional[str] = None
    is_self: bool = False
    user_name: Optional[str] = None
    chat_name: Optional[str] = None

    @classmethod
    async def from_event(cls, event) -> "TelegramMessageAdapter":
        """从 telethon event 创建适配器"""
        sender = await event.get_sender()
        chat = await event.get_chat()
        logger.debug(f"event 消息: \n{json.dumps(event.message.__dict__, default=str, ensure_ascii=False)}")
        logger.debug(f"sender消息: \n{json.dumps(sender.__dict__, default=str, ensure_ascii=False)}")
        logger.debug(f"chat  消息: \n{json.dumps(chat.__dict__, default=str, ensure_ascii=False)}")


        sender_id = getattr(sender, "id", None)
        username = getattr(sender, "username", "")
        first_name = getattr(sender, "first_name", "")
        last_name = getattr(sender, "last_name", "")
        full_name = " ".join(filter(None, [first_name, last_name]))
        user_name = f"{full_name}（@{username}）" if full_name else f"{sender_id}（@{username}）"


        chat_id = getattr(chat, "id", None)
        chat_title = getattr(chat, "title", "")
        chat_name = f'{chat_title}（{chat_id}）' if chat_title else f"聊天（{chat_id}）"
                      

        text = getattr(event.message, "message", "")
        textstrip = text.strip() if text else ""
        command, _, args = (textstrip.partition(" ") if textstrip.startswith("/") else (None, "", None))


        return cls(
            message=event.message,
            text=text,
            sender_id=sender_id,
            chat_id=event.chat_id,
            command=command,
            args=args,
            is_self=event.out,
            user_name=user_name,
            chat_name=chat_name,
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
