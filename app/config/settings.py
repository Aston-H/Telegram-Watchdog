from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from typing import List


class Settings(BaseSettings):
    """应用配置模型"""

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent / ".env"),
        case_sensitive=False,
        extra="ignore",
    )

    # Telegram API 配置
    tg_api_id: int
    tg_api_hash: str
    tg_session_name: str = "Watchdog"

    # 日志配置
    log_level: str = "INFO"
    log_format: str = "%(asctime)s %(levelname)s %(name)s:%(lineno)d: %(message)s"

    # 敏感词配置
    auto_screenshot_switch: bool = True
    sensitive_words_private: List[str] = [
        "您好！这里是ZF-DA组",
        "不定时抽查",
        "各组的值班和远程在线情况",
        "以确保能够及时联系到值班或远程员工。请您在看到此消息后尽快回复，以便我们确认您的在线状态",
    ]
    sensitive_words_group: List[str] = ["日会", "@SimoAwwww"]

    # 告警配置
    private_alert_switch: bool = True
    alert_sound_file: str = "app/config/music.mp3"
    alert_delay_seconds: float = 30.0
    alert_expire_seconds: float = 300.0

    # 群组过滤配置
    filtered_chat_ids: List[int] = [-5025130764]
