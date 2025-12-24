"""
SysDash - Real-time terminal-based system monitoring dashboard
"""

__version__ = "1.0.4"
__author__ = "Thulasiram K"
__all__ = ["MetricsCollector", "CLIDashboard", "MiniDashboard"]

from .collector import MetricsCollector
from .cli import CLIDashboard
from .cli_mini import MiniDashboard
