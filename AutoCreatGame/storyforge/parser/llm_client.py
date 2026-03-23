"""Ollama LLM 客户端 - 封装本地大模型 API 调用"""

from __future__ import annotations

import json
import re

import httpx

from storyforge.config import get_config


class LLMClient:
    """Ollama HTTP API 客户端"""

    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        timeout: float = 300.0,
    ):
        config = get_config()
        self.base_url = (base_url or config.ollama_url).rstrip("/")
        self.model = model or config.model_name
        self.timeout = timeout
        self._client = httpx.Client(timeout=self.timeout)

    def chat(self, system_prompt: str, user_message: str) -> str:
        """发送聊天请求，返回模型回复文本"""
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_predict": 8192,
            },
        }

        resp = self._client.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data["message"]["content"]

    def chat_json(self, system_prompt: str, user_message: str) -> dict | list:
        """发送聊天请求，期望返回 JSON 并解析"""
        # 在 system prompt 中强调 JSON 输出
        json_system = system_prompt + "\n\n重要：你的回复必须是纯 JSON 格式，不要包含 markdown 代码块标记或其他文本。"
        raw = self.chat(json_system, user_message)
        return self._extract_json(raw)

    def check_connection(self) -> bool:
        """检查 Ollama 是否可用"""
        try:
            resp = self._client.get(f"{self.base_url}/api/tags")
            return resp.status_code == 200
        except (httpx.ConnectError, httpx.TimeoutException):
            return False

    def list_models(self) -> list[str]:
        """列出可用模型"""
        try:
            resp = self._client.get(f"{self.base_url}/api/tags")
            resp.raise_for_status()
            data = resp.json()
            return [m["name"] for m in data.get("models", [])]
        except (httpx.ConnectError, httpx.TimeoutException):
            return []

    @staticmethod
    def _extract_json(text: str) -> dict | list:
        """从 LLM 回复中提取 JSON（处理可能的 markdown 包裹）"""
        text = text.strip()

        # 去掉 markdown 代码块
        md_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
        if md_match:
            text = md_match.group(1).strip()

        # 尝试直接解析
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # 尝试找到第一个 { 或 [ 开始的 JSON
        for start_char, end_char in [('{', '}'), ('[', ']')]:
            start = text.find(start_char)
            if start == -1:
                continue
            # 从后往前找匹配的结束符
            end = text.rfind(end_char)
            if end == -1 or end <= start:
                continue
            try:
                return json.loads(text[start:end + 1])
            except json.JSONDecodeError:
                continue

        raise ValueError(f"无法从 LLM 回复中提取有效 JSON:\n{text[:500]}")

    def close(self):
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
