"""
UI Results Subpackage

This subpackage contains UI modules for rendering results and
visualizations of the TCO model calculations.
"""

from ui.results.summary import render_summary
from ui.results.detailed import render_detailed_breakdown
from ui.results.charts import render_charts
from ui.results.display import display_results, display_from_session_state

__all__ = [
    'render_summary',
    'render_detailed_breakdown', 
    'render_charts',
    'display_results',
    'display_from_session_state'
] 