from __future__ import annotations

import json
import urllib.request
from typing import Optional, Protocol


class LLMClient(Protocol):
    """LLM 客户端统一接口。"""

    def generate(self, prompt: str) -> Optional[str]: ...


class OllamaClient:
    """可选本地大模型客户端。未启用或失败时，业务层会自动回退到模板生成。"""

    def __init__(self, model: str, url: str, timeout: int = 60):
        self.model = model
        self.url = url
        self.timeout = timeout

    def generate(self, prompt: str) -> Optional[str]:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read().decode("utf-8")
            obj = json.loads(raw)
            return obj.get("response")
        except Exception:
            return None


class ClaudeClient:
    """Anthropic Messages API 客户端，支持自定义 base_url 兼容其他端点."""

    def __init__(
        self,
        api_key: str,
        model: str = "claude-sonnet-4-6",
        base_url: str | None = None,
        timeout: int = 120,
    ):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.timeout = timeout

    def generate(self, prompt: str) -> Optional[str]:
        try:
            from anthropic import Anthropic

            kwargs = {"api_key": self.api_key, "timeout": self.timeout}
            if self.base_url:
                kwargs["base_url"] = self.base_url
            client = Anthropic(**kwargs)

            message = client.messages.create(
                model=self.model,
                max_tokens=4096,
                system="你是一个专业的地震应急决策辅助AI，基于提供的灾情数据、风险链和图谱证据生成可执行的应急处置策略。语言正式、简洁、可追溯。",
                messages=[{"role": "user", "content": prompt}],
            )
            # 从 content 中提取所有 TextBlock，跳过 ThinkingBlock
            texts = [b.text for b in message.content if hasattr(b, "text")]
            return "".join(texts) if texts else None
        except Exception:
            return None
