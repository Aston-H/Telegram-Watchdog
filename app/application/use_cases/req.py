import httpx
import json
import logging

logger = logging.getLogger(__name__)


class ReqUseCase:
    DEFAULT_URL = "https://cdn.testnet.routescan.io/api/evm/11155111/gas-price"

    async def execute(self, url: str | None = None) -> str:
        target_url = url or self.DEFAULT_URL
        async with httpx.AsyncClient() as client:
            response = await client.get(target_url)
            response.raise_for_status()

            try:
                json_data = response.json()
                return json.dumps(json_data, ensure_ascii=False, indent=2)
            except (json.JSONDecodeError, ValueError) as e:
                logger.info("响应内容不是有效的JSON格式: %s", e)
                return f"响应内容不是有效的JSON格式: {e}"
