"""
工作台服务（Memory 管理、对话上下文、基础编排）

说明：
- 当前实现聚焦于会话管理与基础占位逻辑，后续可接入 content_service / rag_service / image_service 等模块
- 所有会话数据存储在 Redis（见 storage/session_store.py）
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

import dashscope
from dashscope import Generation

from core.config import load_config, AppConfig
from core.logger import logger
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

        # 记录用户消息
        session_store.append_message(self.cfg, payload.session_id, "user", payload.message)

        # 调用通义千问生成内容
        generated = await self._generate_content_with_llm(payload)

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

        # 获取最近的用户消息作为重新生成的依据
        messages = session.get("messages", [])
        last_user_msg = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_user_msg = msg.get("content", "")
                break
        
        dummy_request = WorkspaceSendMessageIn(
            session_id=payload.session_id,
            message=last_user_msg,
            material_source="online",
            platform="xiaohongshu",
        )
        generated = await self._generate_content_with_llm(dummy_request, is_regenerate=True)
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
        self, payload: WorkspaceSendMessageIn, is_regenerate: bool = False
    ) -> WorkspaceContent:
        """
        使用阿里云通义千问生成内容
        """
        # 构建 prompt
        platform_name = "小红书" if payload.platform == "xiaohongshu" else "抖音"
        action = "重新生成" if is_regenerate else "生成"
        
        system_prompt = f"""你是一个专业的{platform_name}内容创作助手。
请根据用户的需求，生成适合{platform_name}平台的爆款内容。
要求：
1. 标题要吸引眼球，适合{platform_name}风格
2. 正文内容要有价值，排版清晰
3. 使用适当的emoji增加可读性
4. 输出格式：第一行是标题，空一行后是正文内容"""

        user_prompt = payload.message if payload.message else "请生成一篇有趣的内容"
        if is_regenerate:
            user_prompt = f"请重新生成：{user_prompt}"

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


