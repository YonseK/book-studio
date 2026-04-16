import pytest

from bookstudio.services.layout import (
    get_layout,
    get_mm_size,
    get_aspect_ratio,
    LAYOUT_PRESETS,
    LayoutConfig,
)


class TestGetLayout:
    def test_pptx_wide_default(self):
        config = get_layout("PPTX_WIDE")
        assert config.width == 1280
        assert config.height == 720

    def test_original_book_preset(self):
        config = get_layout("BOOK")
        assert config.width == 768
        assert config.height == 1086

    def test_all_presets_have_positive_width(self):
        for name, config in LAYOUT_PRESETS.items():
            assert config.width > 0, f"{name} has invalid width"

    def test_custom_preset(self):
        config = get_layout("CUSTOM", custom_width=1920, custom_height=1080)
        assert config.preset == "CUSTOM"
        assert config.width == 1920
        assert config.height == 1080

    def test_custom_defaults(self):
        config = get_layout("CUSTOM")
        assert config.width == 1280
        assert config.height == 720

    def test_unknown_preset_falls_back_to_pptx_wide(self):
        config = get_layout("NONEXISTENT")
        assert config.preset == "PPTX_WIDE"


class TestGetMmSize:
    def test_book_compat(self):
        """원본 BookSize.get_mm_size('BOOK') 호환 검증."""
        result = get_mm_size("BOOK")
        assert result["px_width"] == 768
        assert result["px_height"] == 1086
        assert result["print_width"] == 203.2
        assert abs(result["print_height"] - 287.3375) < 0.01

    def test_mbook_compat(self):
        result = get_mm_size("MBOOK")
        assert result["px_height"] == 960
        assert result["print_height"] == 254.0

    def test_cd_compat(self):
        result = get_mm_size("CD")
        assert result["px_width"] == 768
        assert result["px_height"] == 768

    def test_card_compat(self):
        result = get_mm_size("CARD")
        assert result["px_height"] == 552

    def test_cinema_compat(self):
        result = get_mm_size("CINEMA")
        assert result["px_height"] == 432

    def test_pptx_wide(self):
        result = get_mm_size("PPTX_WIDE")
        assert result["px_width"] == 1280
        assert result["px_height"] == 720


class TestGetAspectRatio:
    def test_pptx_wide_16_9(self):
        assert get_aspect_ratio("PPTX_WIDE") == (16, 9)

    def test_pptx_std_4_3(self):
        assert get_aspect_ratio("PPTX_STD") == (4, 3)

    def test_cd_square(self):
        assert get_aspect_ratio("CD") == (1, 1)

    def test_banner_variable(self):
        assert get_aspect_ratio("BANNER") == (1, 0)
