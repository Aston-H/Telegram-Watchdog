import logging
import asyncio
from tronpy import Tron
from tronpy.providers import HTTPProvider
from tronpy.keys import PrivateKey
from tronpy.contract import Contract

logger = logging.getLogger(__name__)

# TRC20 ABI
TRC20_ABI = [
    {
        "constant": True,
        "inputs": [],
        "name": "name",
        "outputs": [{"name": "", "type": "string"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
    {
        "constant": False,
        "inputs": [
            {"name": "_spender", "type": "address"},
            {"name": "_value", "type": "uint256"},
        ],
        "name": "approve",
        "outputs": [{"name": "", "type": "bool"}],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "totalSupply",
        "outputs": [{"name": "", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
    {
        "constant": False,
        "inputs": [
            {"name": "_from", "type": "address"},
            {"name": "_to", "type": "address"},
            {"name": "_value", "type": "uint256"},
        ],
        "name": "transferFrom",
        "outputs": [{"name": "", "type": "bool"}],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
    {
        "constant": False,
        "inputs": [
            {"name": "_to", "type": "address"},
            {"name": "_value", "type": "uint256"},
        ],
        "name": "transfer",
        "outputs": [{"name": "", "type": "bool"}],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [
            {"name": "_owner", "type": "address"},
            {"name": "_spender", "type": "address"},
        ],
        "name": "allowance",
        "outputs": [{"name": "", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "constructor",
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "_from", "type": "address"},
            {"indexed": True, "name": "_to", "type": "address"},
            {"indexed": False, "name": "_value", "type": "uint256"},
        ],
        "name": "Transfer",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "_owner", "type": "address"},
            {"indexed": True, "name": "_spender", "type": "address"},
            {"indexed": False, "name": "_value", "type": "uint256"},
        ],
        "name": "Approval",
        "type": "event",
    },
]


class BlockchainUseCase:
    """区块链交易用例 - 支持 TRX 和 TRC20 代币转账"""

    def __init__(
        self,
        endpoint_uri: str = "https://nile.trongrid.io/",
        api_key: str = "de828627-4fa5-4e8d-979e-6581338a8719",
        private_key: str = "86b082ae87c41a8b8f4f2641c3260ae79a809e61ed60dab8153d0d6f00ba32e4",
    ):
        self.client = Tron(HTTPProvider(endpoint_uri=endpoint_uri, api_key=api_key))
        self.private_key = PrivateKey(bytes.fromhex(private_key))
        self.from_address = self.private_key.public_key.to_base58check_address()

    async def transfer_trx(self, to_address: str, amount) -> dict:
        """
        转账 TRX

        Args:
            to_address: 接收地址
            amount: 转账金额 (TRX)，可以是 str 或 float

        Returns:
            交易结果信息字典
        """
        try:
            # 确保 amount 是浮点数
            amount_float = float(amount) if isinstance(amount, str) else amount
            logger.info(f"准备转账 {amount_float} TRX 到 {to_address}")

            txn = (
                self.client.trx.transfer(
                    self.from_address, to_address, int(amount_float * 1_000_000)
                )
                .build()
                .sign(self.private_key)
            )

            result = txn.broadcast()
            logger.info(f"广播结果: {result}")

            receipt = result.wait()
            logger.info(f"交易结果: {receipt}")

            return {
                "success": True,
                "txid": txn.txid,
                "from": self.from_address,
                "to": to_address,
                "amount": amount_float,
                "currency": "TRX",
                "receipt": receipt,
            }
        except Exception as e:
            logger.error(f"TRX 转账失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "from": self.from_address,
                "to": to_address,
                "amount": amount,
                "currency": "TRX",
            }

    async def transfer_trc20(
        self,
        to_address: str,
        amount,
        contract_address: str = "TXLAQ63Xg1NAzckPwKHvzw7CSEmLMEqcdj",
        fee_limit: int = 20_000_000,
    ) -> dict:
        """
        转账 TRC20 代币

        Args:
            to_address: 接收地址
            amount: 转账金额，可以是 str 或 float
            contract_address: 代币合约地址
            fee_limit: 手续费上限 (sun，默认 20 TRX)

        Returns:
            交易结果信息字典
        """
        try:
            # 确保 amount 是浮点数
            amount_float = float(amount) if isinstance(amount, str) else amount
            logger.info(
                f"准备转账 {amount_float} TRC20 到 {to_address}，合约: {contract_address}"
            )

            contract = Contract(contract_address, client=self.client, abi=TRC20_ABI)

            txn = (
                contract.functions.transfer(to_address, int(amount_float * 1_000_000))
                .with_owner(self.from_address)
                .fee_limit(fee_limit)
                .build()
                .sign(self.private_key)
            )

            result = txn.broadcast()
            logger.info(f"广播结果: {result}")

            receipt = result.wait()
            logger.info(f"交易结果: {receipt}")

            return {
                "success": True,
                "txid": txn.txid,
                "from": self.from_address,
                "to": to_address,
                "amount": amount_float,
                "currency": "TRC20",
                "contract": contract_address,
                "receipt": receipt,
            }
        except Exception as e:
            logger.error(f"TRC20 转账失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "from": self.from_address,
                "to": to_address,
                "amount": amount,
                "currency": "TRC20",
                "contract": contract_address,
            }

    async def execute(self, args: str) -> dict:
        """
        执行区块链交易

        Args:
            args: 参数字符串，格式: "trx <to_address> <amount>" 或 "trc20 <to_address> <amount> [contract_address]"

        Returns:
            交易结果信息字典
        """
        if not args:
            return {
                "success": False,
                "error": "参数不足，格式: [trx|trc20] <to_address> <amount> [contract_address]",
            }

        # 将字符串参数分割成列表
        arg_list = args.strip().split()

        if len(arg_list) < 3:
            return {
                "success": False,
                "error": "参数不足，格式: [trx|trc20] <to_address> <amount> [contract_address]",
            }

        action = arg_list[0].lower()
        to_address = arg_list[1]
        amount = arg_list[2]  # 保持为字符串，让内部函数处理

        if action == "trx":
            return await self.transfer_trx(to_address, amount)
        elif action == "trc20":
            contract_address = (
                arg_list[3]
                if len(arg_list) > 3
                else "TXLAQ63Xg1NAzckPwKHvzw7CSEmLMEqcdj"
            )
            return await self.transfer_trc20(to_address, amount, contract_address)
        else:
            return {"success": False, "error": "未知的操作类型，必须是 trx 或 trc20"}


if __name__ == "__main__":
    use_case = BlockchainUseCase()

    # 示例：转账 1 TRX 到某地址
    result_trx = asyncio.run(
        use_case.execute("trx TBweH3HtBvAzqoEAFuCzTnz3GKZUSCeztz 1.0")
    )
    print("TRX 转账结果:", result_trx)

    # 示例：转账 0.1 USDT (TRC20) 到某地址
    result_trc20 = asyncio.run(
        use_case.execute(
            "trc20 TBweH3HtBvAzqoEAFuCzTnz3GKZUSCeztz 0.1 TXLAQ63Xg1NAzckPwKHvzw7CSEmLMEqcdj"
        )
    )
    print("TRC20 转账结果:", result_trc20)
