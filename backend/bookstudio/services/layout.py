"""레이아웃/비율 시스템.

원본 BookSize.get_mm_size()를 확장하여 PPTX 프리셋 + 커스텀 비율 지원.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class LayoutConfig:
    """레이아웃 치수 정보."""

    preset: str
    width: int  # px
    height: int  # px
    print_width: Optional[float] = None  # mm
    print_height: Optional[float] = None  # mm
    label: str = ""


# 프리셋 정의: 원본 BookSize + PPTX 표준
LAYOUT_PRESETS: dict[str, LayoutConfig] = {
    # --- PPTX 호환 ---
    "PPTX_WIDE": LayoutConfig(
        preset="PPTX_WIDE",
        width=1280,
        height=720,
        print_width=338.7,
        print_height=190.5,
        label="PPTX Wide 16:9",
    ),
    "PPTX_STD": LayoutConfig(
        preset="PPTX_STD",
        width=960,
        height=720,
        print_width=254.0,
        print_height=190.5,
        label="PPTX Standard 4:3",
    ),
    "PPTX_WP": LayoutConfig(
        preset="PPTX_WP",
        width=720,
        height=1280,
        print_width=190.5,
        print_height=338.7,
        label="PPTX Wide Portrait 9:16",
    ),
    "PPTX_SP": LayoutConfig(
        preset="PPTX_SP",
        width=720,
        height=960,
        print_width=190.5,
        print_height=254.0,
        label="PPTX Standard Portrait 3:4",
    ),
    # --- 원본 BookSize ---
    "BOOK": LayoutConfig(
        preset="BOOK",
        width=768,
        height=1086,
        print_width=203.2,
        print_height=287.3375,
        label="A4 Portrait",
    ),
    "A4_LAND": LayoutConfig(
        preset="A4_LAND",
        width=1086,
        height=768,
        print_width=287.3375,
        print_height=203.2,
        label="A4 Landscape",
    ),
    "MBOOK": LayoutConfig(
        preset="MBOOK",
        width=768,
        height=960,
        print_width=203.2,
        print_height=254.0,
        label="Mini Book",
    ),
    "CD": LayoutConfig(
        preset="CD",
        width=768,
        height=768,
        print_width=203.2,
        print_height=203.2,
        label="Square / CD",
    ),
    "CARD": LayoutConfig(
        preset="CARD",
        width=768,
        height=552,
        print_width=203.2,
        print_height=146.05,
        label="Card",
    ),
    "CINEMA": LayoutConfig(
        preset="CINEMA",
        width=768,
        height=432,
        print_width=203.2,
        print_height=114.3,
        label="Cinema 16:9",
    ),
    "BANNER": LayoutConfig(
        preset="BANNER",
        width=768,
        height=0,  # 가변
        print_width=203.2,
        print_height=None,
        label="Banner (variable height)",
    ),
}


def get_layout(preset: str, custom_width: int = 0, custom_height: int = 0) -> LayoutConfig:
    """프리셋 이름 또는 커스텀 치수로 LayoutConfig 반환."""
    if preset == "CUSTOM":
        return LayoutConfig(
            preset="CUSTOM",
            width=custom_width or 1280,
            height=custom_height or 720,
            label="Custom",
        )
    return LAYOUT_PRESETS.get(preset, LAYOUT_PRESETS["PPTX_WIDE"])


def get_mm_size(book_layout: str) -> dict:
    """원본 BookSize.get_mm_size() 호환 API."""
    config = get_layout(book_layout)
    return {
        "px_width": config.width,
        "print_width": config.print_width,
        "px_height": config.height,
        "print_height": config.print_height,
    }


def get_aspect_ratio(preset: str) -> tuple[int, int]:
    """프리셋의 비율을 (w, h) 튜플로 반환. 예: (16, 9)."""
    from math import gcd

    config = get_layout(preset)
    if config.height == 0:
        return (1, 0)
    d = gcd(config.width, config.height)
    return (config.width // d, config.height // d)
