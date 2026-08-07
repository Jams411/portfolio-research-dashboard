"""Guard professional terminology in public application and report strings."""

import ast
from pathlib import Path
import re


PROHIBITED = re.compile(
    r"\b(?:workbook(?:\s+[123])?|FIN5745|classroom|course|assignment|university|student|instructor|academic template)\b",
    re.IGNORECASE,
)


def public_string_literals(path: str) -> list[str]:
    tree = ast.parse(Path(path).read_text())
    return [
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    ]


def test_public_application_and_report_strings_use_professional_language():
    violations: list[str] = []
    for path in (
        "app.py", "portfolio_dashboard/reporting.py", "portfolio_dashboard/fixed_income_ui.py",
        "portfolio_dashboard/fixed_income.py", "portfolio_dashboard/bond_portfolio.py",
    ):
        for value in public_string_literals(path):
            match = PROHIBITED.search(value)
            if match:
                violations.append(f"{path}: {match.group(0)!r}")
    assert not violations, "Public terminology violations: " + ", ".join(violations)
