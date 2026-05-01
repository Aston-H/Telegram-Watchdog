import logging
from app.config.settings import Settings


def setup_logging() -> None:
    try:
        settings = Settings()
        root_level = getattr(logging, settings.log_level.upper(), logging.INFO)
        telethon_level = getattr(logging, settings.log_level.upper(), logging.WARNING)
        log_format = settings.log_format
        logging.basicConfig(level=root_level, format=log_format)
        logging.getLogger("telethon").setLevel(telethon_level)
    except Exception as e:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(name)s:%(lineno)d: %(message)s",
        )
        logging.error(f"日志配置加载失败，使用默认配置: {e}")
