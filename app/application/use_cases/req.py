import httpx
import json
import logging

logger = logging.getLogger(__name__)


class ReqUseCase:
    DEFAULT_URL = "https://cdn.testnet.routescan.io/api/evm/11155111/gas-price"

    async def execute(self, url: str = None) -> str:
        target_url = url if url else self.DEFAULT_URL
        # 补全协议前缀
        if target_url and not target_url.startswith(('http://', 'https://')):
            target_url = 'https://' + target_url
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(target_url)
                response.raise_for_status()
                try:
                    return json.dumps(response.json(), indent=2, ensure_ascii=False)
                except json.JSONDecodeError:
                    return response.text[:4000]  # 限制返回长度
        except httpx.HTTPError as e:
            logger.error(f"接口请求失败: {e}")
            return f"接口请求失败: {str(e)}"