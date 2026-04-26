"""BookStudio LLM 어댑터 추상 인터페이스."""

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generator


@dataclass
class LLMResponse:
    """LLM 응답."""

    content: str
    model: str = ""
    input_tokens: int = 0
    output_tokens: int = 0


class BaseLLMAdapter(ABC):
    """BookStudio LLM 어댑터 추상 인터페이스."""

    @abstractmethod
    def generate(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 4000,
        response_format: dict | None = None,
    ) -> LLMResponse:
        """동기 완성 생성."""

    @abstractmethod
    def generate_stream(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 4000,
    ) -> Generator[str, None, None]:
        """텍스트 스트리밍 생성. 청크 단위로 yield."""

    def generate_json(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.1,
        max_tokens: int = 4000,
    ) -> tuple[dict, int, int]:
        """JSON 응답 생성. (parsed_dict, input_tokens, output_tokens) 반환."""
        response = self.generate(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
        )
        # 마크다운 코드 블록 제거
        content = response.content.strip()
        if content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
        return json.loads(content), response.input_tokens, response.output_tokens


class BaseImageAdapter(ABC):
    """이미지 생성 어댑터 (Phase 4)."""

    @abstractmethod
    def generate_image(
        self, prompt: str, aspect_ratio: str = "16:9", **kwargs
    ) -> bytes:
        """이미지 생성. bytes 반환."""
