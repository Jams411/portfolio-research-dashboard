"""Regression checks for the native Streamlit theme."""

from pathlib import Path
import tomllib


def _relative_luminance(hex_color: str) -> float:
    channels = [int(hex_color[index:index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4 for value in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def _contrast(first: str, second: str) -> float:
    light, dark = sorted((_relative_luminance(first), _relative_luminance(second)), reverse=True)
    return (light + 0.05) / (dark + 0.05)


def test_streamlit_theme_is_dark_and_accessible():
    config = tomllib.loads(Path(".streamlit/config.toml").read_text())
    theme = config["theme"]
    assert theme["base"] == "dark"
    assert _contrast(theme["textColor"], theme["backgroundColor"]) >= 4.5
    assert _contrast("#FFFFFF", theme["primaryColor"]) >= 4.5
    assert len(theme["chartCategoricalColors"]) >= 6
    assert len(theme["chartSequentialColors"]) == 10
