import logging
from typing import List

logger = logging.getLogger(__name__)


def contains_sensitive_word(text: str, words: List[str]) -> bool:
    """检查文本是否包含敏感词"""
    for word in words:
        if word in text:
            logger.info("检测到敏感词: %s", word)
            return True
    return False
