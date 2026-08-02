"""Deployment-facing import contracts for the PortfolioLens analytics package."""

from importlib import import_module
from pathlib import Path
import pkgutil
import sys

import portfolio_dashboard


def test_every_tracked_package_module_imports_from_the_repository():
    """Catch missing modules and stale package paths before deployment."""
    package_root = Path(portfolio_dashboard.__file__).resolve().parent
    module_names = {
        module.name
        for module in pkgutil.iter_modules(portfolio_dashboard.__path__, "portfolio_dashboard.")
    }
    assert "portfolio_dashboard.formatting" in module_names

    for module_name in sorted(module_names):
        module = import_module(module_name)
        assert sys.modules[module_name] is module
        assert Path(module.__file__).resolve().is_relative_to(package_root)
