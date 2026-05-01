class StartUseCase:
    """开始命令用例"""

    def execute(self) -> str:
        """执行用例"""
        return "欢迎使用 Telegram Watchdog！\n\n可用命令：\n/start - 开始\n/help - 帮助\n/b - 区块链信息\n/req - 接口信息"
