"""Display formatting shared by Streamlit views."""
import math

def pct(value: float, decimals: int = 2) -> str:
    return "N/A" if value is None or not math.isfinite(float(value)) else f"{float(value):.{decimals}%}"

def ratio(value: float, decimals: int = 2) -> str:
    return "N/A" if value is None or not math.isfinite(float(value)) else f"{float(value):.{decimals}f}"

def money(value: float) -> str:
    return "N/A" if value is None or not math.isfinite(float(value)) else f"${float(value):,.2f}"
