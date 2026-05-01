from __future__ import annotations

from typing import Callable, Dict, Optional

from app.adapters.telegram.message_handler import TelegramMessageAdapter

Handler = Callable[[TelegramMessageAdapter], object]


class Router:
    def __init__(self) -> None:
        self._routes: Dict[str, Handler] = {}

    def _normalize(self, command: str) -> str:
        return command.strip().lower()

    def register(self, command: str, handler: Handler) -> None:
        self._routes[self._normalize(command)] = handler

    def resolve(self, command: Optional[str]) -> Optional[Handler]:
        if not command:
            return None
        return self._routes.get(self._normalize(command))
