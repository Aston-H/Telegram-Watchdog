import asyncio
import sys
import os
import logging
from typing import Optional, Dict
from datetime import datetime, timedelta
from dataclasses import dataclass
from app.adapters.telegram.message_handlers.audio_handler import AUDIO_HANDLER

logger = logging.getLogger(__name__)

# 添加项目根目录到 Python 路径，支持直接运行
try:
    from app.adapters.telegram.message_handler import TelegramMessageAdapter
except ImportError:
    # 如果直接运行脚本，添加项目根目录到路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
    )
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    from app.adapters.telegram.message_handler import TelegramMessageAdapter


@dataclass
class AlertTask:
    """告警任务数据结构"""

    chat_id: int
    task: asyncio.Task
    alert_state: bool = True  # 告警状态：True=需要告警，False=已告警
    created_at: datetime = None
    last_updated: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.last_updated is None:
            self.last_updated = self.created_at


class AlertManager:
    """告警任务管理器"""

    def __init__(
        self,
        delay_seconds: float = 30.0,
        cleanup_interval: float = 60.0,
        task_expire_seconds: float = 300.0,
    ):
        """
        初始化告警管理器

        Args:
            delay_seconds: 告警延迟秒数（默认30秒）
            cleanup_interval: 自动清理间隔秒数（默认60秒）
            task_expire_seconds: 任务过期秒数（默认300秒）
        """
        self.delay_seconds = delay_seconds
        self.cleanup_interval = cleanup_interval
        self.task_expire_seconds = task_expire_seconds

        self._alert_tasks: Dict[int, AlertTask] = {}
        self._cleanup_task: Optional[asyncio.Task] = None
        self._is_cleanup_running = False

    def start_cleanup(self) -> None:
        """启动自动清理任务"""
        if not self._is_cleanup_running:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            self._is_cleanup_running = True

    def stop_cleanup(self) -> None:
        """停止自动清理任务"""
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
        self._is_cleanup_running = False

    async def _cleanup_loop(self) -> None:
        """自动清理循环"""
        try:
            while True:
                await asyncio.sleep(self.cleanup_interval)
                self.cleanup_tasks()
        except asyncio.CancelledError:
            pass

    def trigger_alert(self, message: TelegramMessageAdapter) -> None:
        """
        触发告警

        逻辑：
        1. 为每个chat_id创建延迟任务（30秒后播放音效）
        2. 未播放音效前，又触发trigger_alert()，告警状态置为true，延迟更新30s后告警
        3. 播放完音效后，告警状态置为false
        4. 未清理的任务，又触发trigger_alert()，告警状态不更新，跳过，直到任务被清理
        """
        chat_id = message.chat_id

        if chat_id in self._alert_tasks:
            alert_task = self._alert_tasks[chat_id]

            if not alert_task.task.done():
                # 任务未完成，取消当前任务，重新创建
                alert_task.task.cancel()
                alert_task.alert_state = True  # 告警状态置为true
                alert_task.last_updated = datetime.now()

                # 创建新的延迟任务
                new_task = asyncio.create_task(self._delayed_alert(chat_id))
                alert_task.task = new_task
                logger.info(f"Chat {chat_id}: 更新告警延迟，30秒后播放音效")
            else:
                # 任务已完成，检查是否需要重新告警
                if alert_task.alert_state:
                    # 告警状态为true但任务已完成，说明音效已播放
                    alert_task.alert_state = False
                    logger.info(f"Chat {chat_id}: 音效已播放，告警状态置为false")
                else:
                    # 告警状态为false，未清理的任务，跳过不更新
                    logger.info(f"Chat {chat_id}: 任务已完成但未清理，跳过触发")
        else:
            # 新chat_id，创建告警任务
            self._create_new_alert_task(chat_id)
            logger.info(f"Chat {chat_id}: 创建告警任务，30秒后播放音效")

    def _create_new_alert_task(self, chat_id: int) -> None:
        """创建新的告警任务"""
        task = asyncio.create_task(self._delayed_alert(chat_id))
        alert_task = AlertTask(
            chat_id=chat_id,
            task=task,
            alert_state=True,
            created_at=datetime.now(),
            last_updated=datetime.now(),
        )
        self._alert_tasks[chat_id] = alert_task

    async def _delayed_alert(self, chat_id: int) -> None:
        """延迟告警执行"""
        await asyncio.sleep(self.delay_seconds)

        # 检查任务是否仍然存在且告警状态为true
        if chat_id in self._alert_tasks and self._alert_tasks[chat_id].alert_state:
            # 播放音效
            AUDIO_HANDLER.play_audio(volume=0.5, loop=3)

            # 播放完音效后，告警状态置为false
            self._alert_tasks[chat_id].alert_state = False
            logger.info(f"Chat {chat_id}: 音效播放完成，告警状态置为false")

    def get_alert_state(self, chat_id: int) -> Optional[bool]:
        """获取指定chat_id的告警状态"""
        if chat_id in self._alert_tasks:
            return self._alert_tasks[chat_id].alert_state
        return None

    def cleanup_tasks(self) -> None:
        """清理超过300秒前的任务"""
        now = datetime.now()
        expired_chats = []

        for chat_id, alert_task in self._alert_tasks.items():
            # 检查任务是否过期（超过task_expire_seconds秒）
            if (
                now - alert_task.last_updated
            ).total_seconds() > self.task_expire_seconds:
                # 取消任务
                if not alert_task.task.done():
                    alert_task.task.cancel()
                expired_chats.append(chat_id)
                logger.info(f"Chat {chat_id}: 任务过期，已清理")

        # 清理过期任务
        for chat_id in expired_chats:
            del self._alert_tasks[chat_id]

        logger.info(
            f"清理完成：清理了 {len(expired_chats)} 个过期任务，剩余 {len(self._alert_tasks)} 个任务"
        )

    def get_task_count(self) -> int:
        """获取当前任务数量"""
        return len(self._alert_tasks)

    def get_active_task_count(self) -> int:
        """获取活跃任务数量（告警状态为true的任务）"""
        return sum(1 for task in self._alert_tasks.values() if task.alert_state)


# 全局告警管理器实例
ALERT_MANAGER = AlertManager()


if __name__ == "__main__":
    # 测试重构后的告警逻辑
    import time
    import asyncio

    class MockMessage:
        def __init__(self, chat_id):
            self.chat_id = chat_id

    async def run_test():
        logger.info("=== 告警逻辑测试 ===\n")

        # 创建测试管理器，使用较短时间便于测试
        alert_manager = AlertManager(
            delay_seconds=2.0, cleanup_interval=5.0, task_expire_seconds=10.0
        )
        alert_manager.start_cleanup()

        logger.info("1. 首次触发告警 - Chat 123")
        alert_manager.trigger_alert(MockMessage(chat_id=123))
        logger.info(f"   告警状态: {alert_manager.get_alert_state(123)}")

        logger.info("\n2. 1秒后再次触发 - 应延迟更新")
        await asyncio.sleep(1)
        alert_manager.trigger_alert(MockMessage(chat_id=123))
        logger.info(f"   告警状态: {alert_manager.get_alert_state(123)}")

        logger.info("\n3. 等待3秒让音效播放")
        await asyncio.sleep(3)
        logger.info(f"   告警状态: {alert_manager.get_alert_state(123)}")

        logger.info("\n4. 播放完成后再次触发 - 应跳过（任务未清理）")
        alert_manager.trigger_alert(MockMessage(chat_id=123))
        logger.info(f"   告警状态: {alert_manager.get_alert_state(123)}")

        logger.info("\n5. 测试其他chat_id")
        alert_manager.trigger_alert(MockMessage(chat_id=456))
        alert_manager.trigger_alert(MockMessage(chat_id=789))
        logger.info(f"   任务总数: {alert_manager.get_task_count()}")
        logger.info(f"   活跃任务数: {alert_manager.get_active_task_count()}")

        logger.info("\n6. 等待清理任务执行（5秒间隔）")
        await asyncio.sleep(6)
        logger.info(f"   清理后任务总数: {alert_manager.get_task_count()}")

        logger.info("\n7. 任务清理后再次触发 - 应创建新任务")
        alert_manager.trigger_alert(MockMessage(chat_id=123))
        logger.info(f"   告警状态: {alert_manager.get_alert_state(123)}")
        logger.info(f"   任务总数: {alert_manager.get_task_count()}")

        logger.info("\n8. 停止清理任务")
        alert_manager.stop_cleanup()
        await asyncio.sleep(1)

        logger.info("\n=== 测试完成 ===")

    asyncio.run(run_test())
