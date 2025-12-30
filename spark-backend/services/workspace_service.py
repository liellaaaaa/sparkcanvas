"""
工作台服务（Memory 管理、对话上下文、基础编排）

说明：
- 当前实现聚焦于会话管理与基础占位逻辑，后续可接入 content_service / rag_service / image_service 等模块
- 所有会话数据存储在 Redis（见 storage/session_store.py）
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional, List

import dashscope
from dashscope import Generation

from core.config import load_config, AppConfig
from core.logger import logger
from services.search_service import tavily_search
from services.rag_service import RAGService
from services.prompt_loader import PromptLoader, PromptNotFoundError
from schemas.workspace import (
    WorkspaceSessionCreateOut,
    WorkspaceSendMessageIn,
    WorkspaceSendMessageOut,
    WorkspaceContent,
    WorkspaceSessionInfoOut,
    WorkspaceRegenerateIn,
    WorkspaceRegenerateOut,
)
from storage import session_store, history_store
from utils.response import APIResponse, success_response


_cfg: AppConfig = load_config()


def _now_iso() -> str:
    """当前时间 ISO8601 字符串（秒级，UTC）"""
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


class WorkspaceService:
    """
    工作台服务

    职责：
    - 会话创建与查询
    - 消息记录（user / assistant）
    - 调用内容生成引擎（当前为占位实现，后续接入 content_service 等模块）
    """

    def __init__(self, cfg: AppConfig | None = None) -> None:
        self.cfg = cfg or _cfg
        self.prompt_loader = PromptLoader()

    # ------------------------- 会话相关 -------------------------

    async def create_session(self, user_id: int) -> APIResponse:
        """
        创建新会话

        Args:
            user_id: 当前用户ID（暂未入库存储，后续可绑定到会话）
        """
        data = session_store.create_session(self.cfg)
        logger.info(f"[Workspace] user_id={user_id} 创建会话 session_id={data['session_id']}")
        out = WorkspaceSessionCreateOut(**data)
        return success_response(out)

    async def get_session_info(self, session_id: str) -> Optional[WorkspaceSessionInfoOut]:
        """
        获取会话信息
        """
        raw = session_store.get_session(self.cfg, session_id)
        if not raw:
            return None
        messages = raw.get("messages", [])
        last_message_time = messages[-1].get("timestamp") if messages else None
        return WorkspaceSessionInfoOut(
            session_id=raw["session_id"],
            created_at=raw["created_at"],
            expires_at=raw["expires_at"],
            message_count=len(messages),
            last_message_time=last_message_time,
        )

    # ------------------------- 消息与生成 -------------------------

    async def send_message(self, user_id: int, payload: WorkspaceSendMessageIn) -> APIResponse:
        """
        发送消息到工作台

        当前实现：
        - 校验会话是否存在
        - 记录 user 消息
        - 使用占位逻辑生成内容（简单 echo 文本）
        - 记录 assistant 消息
        """
        session = session_store.get_session(self.cfg, payload.session_id)
        if not session:
            from fastapi import HTTPException

            raise HTTPException(status_code=404, detail="会话不存在或已过期")

        # 记录用户消息（同时保存素材源和平台信息，供重新生成时使用）
        session_store.append_message(
            self.cfg, 
            payload.session_id, 
            "user", 
            payload.message,
            metadata={"material_source": payload.material_source, "platform": payload.platform}
        )

        # 联网搜索：仅在素材源为 online 时执行
        search_snippets = await self._maybe_online_search(payload)
        
        # RAG知识库检索：仅在素材源为 rag 时执行
        rag_snippets = await self._maybe_rag_search(user_id, payload)

        # 调用通义千问生成内容（优先使用RAG检索结果）
        generated = await self._generate_content_with_llm(payload, search_snippets, rag_snippets)

        # 记录助手消息
        assistant_text = f"{generated.title}\n\n{generated.body}"
        session_store.append_message(self.cfg, payload.session_id, "assistant", assistant_text)

        # 保存到历史记录
        try:
            history_store.save_conversation_history(
                self.cfg,
                user_id,
                payload.session_id,
                payload.message,
                assistant_text,
            )
        except Exception as e:
            # 历史记录保存失败不影响主流程，仅记录日志
            logger.warning(f"[Workspace] 保存历史记录失败: {e}")

        out = WorkspaceSendMessageOut(
            session_id=payload.session_id,
            content=generated,
            status="completed",
            timestamp=_now_iso(),
        )
        logger.info(
            f"[Workspace] user_id={user_id} session_id={payload.session_id} "
            f"发送消息并完成占位生成"
        )
        return success_response(out)

    async def regenerate(self, user_id: int, payload: WorkspaceRegenerateIn) -> APIResponse:
        """
        基于已有会话重新生成内容

        当前实现：
        - 校验会话是否存在
        - 使用占位逻辑重新生成（不改变历史消息，仅追加一条 assistant 消息）
        """
        session = session_store.get_session(self.cfg, payload.session_id)
        if not session:
            from fastapi import HTTPException

            raise HTTPException(status_code=404, detail="会话不存在或已过期")

        # 这里可以根据 adjustments 调整生成逻辑，当前仅做记录
        logger.info(
            f"[Workspace] user_id={user_id} session_id={payload.session_id} "
            f"重新生成，adjustments={payload.adjustments}"
        )

        # 获取最近的用户消息和素材源作为重新生成的依据
        messages = session.get("messages", [])
        last_user_msg = ""
        last_material_source = "online"  # 默认值
        last_platform = "xiaohongshu"  # 默认值
        
        # 从会话历史中查找最近的用户消息和对应的素材源
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_user_msg = msg.get("content", "")
                # 尝试从消息元数据中获取素材源和平台（如果之前保存过）
                if "material_source" in msg:
                    last_material_source = msg.get("material_source", "online")
                if "platform" in msg:
                    last_platform = msg.get("platform", "xiaohongshu")
                break
        
        dummy_request = WorkspaceSendMessageIn(
            session_id=payload.session_id,
            message=last_user_msg,
            material_source=last_material_source,
            platform=last_platform,
        )
        search_snippets = await self._maybe_online_search(dummy_request)
        rag_snippets = await self._maybe_rag_search(user_id, dummy_request)
        generated = await self._generate_content_with_llm(
            dummy_request, search_snippets, rag_snippets, is_regenerate=True
        )
        assistant_text = f"{generated.title}\n\n{generated.body}"
        session_store.append_message(self.cfg, payload.session_id, "assistant", assistant_text)

        # 保存到历史记录
        try:
            history_store.save_conversation_history(
                self.cfg,
                user_id,
                payload.session_id,
                last_user_msg,
                assistant_text,
            )
        except Exception as e:
            # 历史记录保存失败不影响主流程，仅记录日志
            logger.warning(f"[Workspace] 保存历史记录失败: {e}")

        out = WorkspaceRegenerateOut(
            session_id=payload.session_id,
            content=generated,
            status="completed",
            timestamp=_now_iso(),
        )
        return success_response(out)

    # ------------------------- 内部方法 -------------------------

    async def _generate_content_with_llm(
        self,
        payload: WorkspaceSendMessageIn,
        search_snippets: Optional[List[str]] = None,
        rag_snippets: Optional[List[str]] = None,
        is_regenerate: bool = False,
    ) -> WorkspaceContent:
        """
        使用阿里云通义千问生成内容
        """
        # 平台映射：前端传入的平台标识 -> prompts 目录中的平台名称
        if payload.platform == "xiaohongshu":
            platform_name = "小红书"
            prompt_platform = "xhs"
        elif payload.platform == "douyin":
            platform_name = "抖音"
            prompt_platform = "douyin"
        else:
            platform_name = payload.platform or "内容平台"
            prompt_platform = "global"

        action = "重新生成" if is_regenerate else "生成"

        # 选择模式：目前简单按平台使用 default，后续可根据业务扩展为 short_video 等
        prompt_mode = "default"

        # 尝试从 prompts 目录加载带占位符的 system prompt，失败则回退到内置模板
        try:
            variables = {
                # TODO: 如需可从用户信息中注入真实昵称 / 品牌名等
                "username": "",
                "brand_name": "",
                "target_audience": "",
                "video_topic": "",
                "user_requirement": payload.message or "",
            }
            prompt_result = self.prompt_loader.load_prompt(
                platform=prompt_platform,
                mode=prompt_mode,
                variables=variables,
            )
            system_prompt = prompt_result.content
            logger.info(
                f"[Workspace] 使用 prompts/{prompt_platform}/{prompt_mode}.prompt 作为 system prompt",
            )
        except (PromptNotFoundError, ValueError) as e:
            logger.warning(
                f"[Workspace] Prompt 加载失败，使用内置 system_prompt: {e}",
            )
            system_prompt = (
                f"你是一个专业的{platform_name}内容创作助手。\n"
                f"请根据用户的需求，生成适合{platform_name}平台的爆款内容。\n"
                "要求：\n"
                f"1. 标题要吸引眼球，适合{platform_name}风格\n"
                "2. 正文内容要有价值，排版清晰\n"
                "3. 使用适当的emoji增加可读性\n"
                "4. 输出格式：第一行是标题，空一行后是正文内容"
            )

        user_prompt = payload.message if payload.message else "请生成一篇有趣的内容"
        if is_regenerate:
            user_prompt = f"请重新生成：{user_prompt}"

        # 优先使用RAG知识库检索结果，如果存在则优先使用
        rag_snippets = rag_snippets or []
        search_snippets = search_snippets or []
        
        if rag_snippets:
            # 使用RAG知识库内容（优先）
            merged_rag = "\n".join(f"- {item}" for item in rag_snippets)
            user_prompt = (
                f"{user_prompt}\n\n"
                f"【知识库内容】以下是从RAG知识库中检索到的相关内容，请优先基于这些内容进行创作：\n"
                f"{merged_rag}"
            )
            # 如果同时有联网搜索结果，也一并提供作为补充
            if search_snippets:
                merged_search = "\n".join(f"- {item}" for item in search_snippets)
                user_prompt += (
                    f"\n\n【联网搜索摘要】以下是与主题相关的最新检索结果，可作为补充参考：\n"
                    f"{merged_search}"
                )
        elif search_snippets:
            # 仅使用联网搜索结果
            merged_snippets = "\n".join(f"- {item}" for item in search_snippets)
            user_prompt = (
                f"{user_prompt}\n\n"
                f"【联网搜索摘要】以下是与主题相关的最新检索结果，请结合摘要创作：\n"
                f"{merged_snippets}"
            )

        # 设置 API Key
        dashscope.api_key = self.cfg.dashscope_api_key

        try:
            response = Generation.call(
                model=self.cfg.dashscope_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.cfg.dashscope_temperature,
                result_format="message",
            )

            if response.status_code == 200:
                content_text = response.output.choices[0].message.content
                # 解析标题和正文
                lines = content_text.strip().split("\n", 1)
                title = lines[0].strip().lstrip("#").strip() if lines else f"[{platform_name}] 生成内容"
                body = lines[1].strip() if len(lines) > 1 else content_text
                
                logger.info(f"[Workspace] 通义千问生成成功，model={self.cfg.dashscope_model}")
                return WorkspaceContent(title=title, body=body, image_url=None)
            else:
                logger.error(f"[Workspace] 通义千问调用失败: {response.code} - {response.message}")
                return self._generate_fallback_content(payload, is_regenerate, f"API错误: {response.message}")

        except Exception as e:
            logger.error(f"[Workspace] 通义千问异常: {e}")
            return self._generate_fallback_content(payload, is_regenerate, str(e))

    def _generate_fallback_content(
        self, payload: WorkspaceSendMessageIn, is_regenerate: bool, error_msg: str
    ) -> WorkspaceContent:
        """降级内容（LLM 调用失败时使用）"""
        platform_name = "小红书" if payload.platform == "xiaohongshu" else "抖音"
        action = "重新生成" if is_regenerate else "生成"
        title = f"[{platform_name}] {action}失败 - 降级内容"
        body = f"抱歉，内容生成遇到问题：{error_msg}\n\n请稍后重试。"
        return WorkspaceContent(title=title, body=body, image_url=None)

    # ------------------------- 辅助：联网搜索 -------------------------
    async def _maybe_online_search(self, payload: WorkspaceSendMessageIn) -> List[str]:
        """
        当素材来源为 online 时，通过 Tavily 联网搜索返回简短摘要列表。
        """
        if payload.material_source != "online":
            return []

        results = await tavily_search(payload.message, self.cfg)
        if not results:
            return []

        # 只取前3条，截断每条摘要长度，避免 prompt 过长
        snippets: List[str] = []
        for item in results[:3]:
            title = item.get("title", "").strip()
            summary = item.get("content", "").strip()
            url = item.get("url", "").strip()
            combined = f"{title} | {summary}"
            if len(combined) > 400:
                combined = combined[:400] + "..."
            if url:
                combined = f"{combined} （来源：{url}）"
            snippets.append(combined)

        logger.info(f"[Workspace] 联网搜索注入 {len(snippets)} 条摘要供生成使用")
        return snippets

    # ------------------------- 辅助：RAG知识库检索 -------------------------
    async def _maybe_rag_search(
        self, user_id: int, payload: WorkspaceSendMessageIn
    ) -> List[str]:
        """
        当素材来源为 rag 时，通过RAG知识库进行语义检索，返回相关文档片段列表。
        
        Args:
            user_id: 用户ID
            payload: 工作台消息请求
            
        Returns:
            检索到的文档片段列表（字符串列表）
        """
        if payload.material_source != "rag":
            return []

        try:
            rag_service = RAGService(self.cfg)
            search_result = await rag_service.search(
                user_id=user_id,
                query=payload.message,
                top_k=5,  # 返回Top-5最相关的文档片段
            )
            
            if not search_result or not search_result.results:
                logger.info(f"[Workspace] RAG知识库检索无结果，query={payload.message}")
                return []
            
            # 提取文档内容，格式化后返回
            snippets: List[str] = []
            for result in search_result.results:
                content = result.content.strip()
                # 截断过长的内容，避免prompt过长
                if len(content) > 500:
                    content = content[:500] + "..."
                
                # 添加元数据信息（文件名等）
                metadata = result.metadata or {}
                file_name = metadata.get("file_name", "未知文档")
                snippet = f"{content}（来源：{file_name}）"
                snippets.append(snippet)
            
            logger.info(
                f"[Workspace] RAG知识库检索成功，user_id={user_id}, "
                f"query={payload.message}, 返回{len(snippets)}条片段"
            )
            return snippets
            
        except Exception as e:
            # RAG检索失败不影响主流程，仅记录日志
            logger.warning(f"[Workspace] RAG知识库检索失败: {e}")
            return []


