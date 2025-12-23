"""
联网搜索服务（Tavily）

职责：
- 调用 Tavily Search API 获取最新的公开网页摘要
- 对外暴露统一的异步接口，便于工作台等模块复用
"""
from __future__ import annotations

from typing import Any, Dict, List

import httpx

from core.config import AppConfig
from core.logger import logger


TAVILY_ENDPOINT = "https://api.tavily.com/search"


async def tavily_search(
    query: str,
    cfg: AppConfig,
    *,
    max_results: int = 5,
    search_depth: str = "advanced",
    timeout: float = 10.0,
) -> List[Dict[str, Any]]:
    """
    调用 Tavily 搜索，返回结构化结果列表。

    Args:
        query: 搜索关键词
        cfg: 全局配置，提供 Tavily API Key
        max_results: 返回结果数量（默认5条）
        search_depth: 搜索深度，默认为 advanced
        timeout: 请求超时时间（秒）

    Returns:
        结构化结果列表，字段包含 title/url/content。失败时返回空列表。
    """
    if not cfg.tavily_api_key:
        logger.warning("[Tavily] 未配置 API Key，跳过联网搜索")
        return []

    payload = {
        "api_key": cfg.tavily_api_key,
        "query": query,
        "max_results": max_results,
        "search_depth": search_depth,
    }

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(TAVILY_ENDPOINT, json=payload)
        if resp.status_code != 200:
            logger.error(f"[Tavily] 请求失败 status={resp.status_code} body={resp.text}")
            return []
        data = resp.json()
        results = data.get("results", [])
        parsed: List[Dict[str, Any]] = []
        for item in results:
            parsed.append(
                {
                    "title": item.get("title") or "",
                    "url": item.get("url") or "",
                    "content": item.get("content") or "",
                }
            )
        logger.info(f"[Tavily] 搜索成功，返回 {len(parsed)} 条结果")
        return parsed
    except Exception as exc:  # 网络异常统一捕获
        logger.error(f"[Tavily] 调用异常: {exc}")
        return []


