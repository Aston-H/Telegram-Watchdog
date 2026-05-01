import sys
from pathlib import Path

# 添加项目根目录到 Python 路径，支持直接运行
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.adapters.telegram.client import TelegramClientWrapper
from app.adapters.telegram.event_adapter import TelegramEventAdapter
from app.config.settings import Settings
from app.core.dispatcher import Dispatcher
from app.core.router import Router
from app.logging_config import setup_logging
from app.modules.user.routes import register_user_routes


def create_application() -> TelegramEventAdapter:
    """创建并配置应用"""
    setup_logging()

    router = Router()
    register_user_routes(router)
    dispatcher = Dispatcher(router)

    settings = Settings()
    client_wrapper = TelegramClientWrapper(
        api_id=settings.tg_api_id,
        api_hash=settings.tg_api_hash,
        session_name=settings.tg_session_name,
    )

    return TelegramEventAdapter(client_wrapper, dispatcher)


def main() -> None:
    """应用主入口"""
    app = create_application()
    app.start()


if __name__ == "__main__":
    main()
