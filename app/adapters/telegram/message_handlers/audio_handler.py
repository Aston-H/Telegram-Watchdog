import subprocess
import asyncio
import time
from typing import Optional
from collections import deque


class AudioHandler:
    """音效处理器 - 支持队列、系统音量管理"""

    def __init__(self):
        self._is_playing = False  # 是否正在播放
        self._current_process: Optional[subprocess.Popen] = None  # 当前播放的子进程
        self._play_queue = deque()  # 播放队列
        self._queue_processing = False  # 队列处理中
        self._system_volume_backup: Optional[float] = None  # 备份的系统音量

    def _get_system_volume(self) -> float:
        """获取系统音量（0.0-1.0）"""
        try:
            result = subprocess.run(
                ["osascript", "-e", "output volume of (get volume settings)"],
                capture_output=True,
                text=True,
                timeout=2,
            )
            if result.returncode == 0:
                return float(result.stdout.strip()) / 100
        except Exception as e:
            print(f"获取系统音量失败: {e}")
        return 1.0

    def _set_system_volume(self, volume: float) -> bool:
        """设置系统音量（0.0-1.0）"""
        try:
            volume_percent = max(0, min(100, int(volume * 100)))
            subprocess.run(
                ["osascript", "-e", f"set volume output volume {volume_percent}"],
                timeout=2,
            )
            return True
        except Exception as e:
            print(f"设置系统音量失败: {e}")
        return False

    def _wait_for_process_completion(self, timeout: int = 300) -> bool:
        """等待当前进程完成播放，返回是否成功"""
        if not self._current_process:
            return True
        try:
            self._current_process.wait(timeout=timeout)
            return True
        except subprocess.TimeoutExpired:
            self._current_process.terminate()
            return False

    def _process_queue_sync(self) -> None:
        """同步处理播放队列"""
        if self._queue_processing:
            return

        self._queue_processing = True
        while self._play_queue and not self._is_playing:
            task = self._play_queue.popleft()
            self._process_sync(task["sound_file"], task["volume"], task["loop"])
            # 等待一段时间再处理下一个，给系统反应时间
            time.sleep(0.5)
        self._queue_processing = False

    def play_audio(
        self, sound_file: Optional[str] = None, volume: float = 0.3, loop: int = 1
    ) -> None:
        """播放音效 (支持队列，若有进程则延后播放)

        Args:
            sound_file: 音效文件路径，默认为 '/System/Library/Sounds/Hero.aiff'
            volume: 播放音量 (0.0-1.0)，默认为 0.1
            loop: 循环次数，默认为 1（1 为单次，-1 为无限循环）
        """
        # 参数默认值
        sound_file = sound_file or "/System/Library/Sounds/Hero.aiff"
        volume = max(0.0, min(1.0, volume))  # 限制音量在 0-1 之间
        loop = loop if loop > 0 else 1  # 至少循环一次

        # 将任务加入队列
        self._play_queue.append(
            {"sound_file": sound_file, "volume": volume, "loop": loop}
        )

        # 如果当前没有播放，立即处理队列
        if not self._is_playing and not self._queue_processing:
            self._process_queue_sync()

    def _process_sync(self, sound_file: str, volume: float, loop: int) -> None:
        """同步播放（没有事件循环时使用）"""
        self._is_playing = True

        # 备份并设置新的系统音量
        self._system_volume_backup = self._get_system_volume()
        self._set_system_volume(volume)

        try:
            # 循环播放
            for i in range(loop):
                cmd = ["afplay", sound_file]
                self._current_process = subprocess.Popen(cmd)
                print(
                    f"正在播放音效: {sound_file} (音量: {volume:.1f}, 循环 {i+1}/{loop})"
                )
                self._wait_for_process_completion()
        except Exception as e:
            print(f"播放音效失败: {e}")
        finally:
            if self._system_volume_backup is not None:
                self._set_system_volume(self._system_volume_backup)
                self._system_volume_backup = None

            self._is_playing = False
            self._current_process = None

    def stop_audio(self) -> None:
        """停止播放音效"""
        if self._is_playing and self._current_process:
            self._current_process.terminate()
            self._is_playing = False
            print("已停止播放音效")

        # 恢复系统音量
        if self._system_volume_backup is not None:
            self._set_system_volume(self._system_volume_backup)
            self._system_volume_backup = None

    def is_playing(self) -> bool:
        """检查是否正在播放音效"""
        return self._is_playing

    def queue_size(self) -> int:
        """获取播放队列中的任务数"""
        return len(self._play_queue)


# 全局音效处理器实例
AUDIO_HANDLER = AudioHandler()

if __name__ == "__main__":
    # 示例用法：多个来源调用
    print("测试 1: 默认参数播放")
    AUDIO_HANDLER.play_audio()
    # 等待播放完成
    while AUDIO_HANDLER.is_playing():
        time.sleep(0.1)

    time.sleep(1)

    print("\n测试 2: 自定义音量")
    AUDIO_HANDLER.play_audio(volume=0.5, loop=3)
    while AUDIO_HANDLER.is_playing():
        time.sleep(0.1)

    time.sleep(1)

    print("\n测试 3: 队列测试 - 连续调用多次")
    AUDIO_HANDLER.play_audio(volume=0.3)
    AUDIO_HANDLER.play_audio(volume=0.7)
    print(f"队列中有 {AUDIO_HANDLER.queue_size()} 个任务")
    while AUDIO_HANDLER.is_playing():
        time.sleep(0.1)
