from app.core.router import Router
from app.modules.user.handler import UserCommandHandler


def register_user_routes(router: Router) -> None:
    """注册用户相关路由"""
    handler = UserCommandHandler()
    router.register("/start", handler.handle_start)
    router.register("/help", handler.handle_help)
    router.register("/screenshot", handler.handle_screenshot)
    router.register("/req", handler.handle_req)
    router.register("/b", handler.handle_blockchain)
