class HelpUseCase:
    """帮助命令用例"""

    def execute(self) -> str:
        """执行用例"""
        return """Telegram Watchdog 使用说明：
/start - 欢迎信息
/req - 接口信息
/b - 区块链信息（支持 /trx 和 /erc20）
"""
