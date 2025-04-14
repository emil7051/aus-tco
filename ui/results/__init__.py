"""
Results Module

This module provides components for displaying TCO results, charts, and analysis.
"""

from ui.results.display import display_results, display_from_session_state
from ui.results.charts import render_charts
from ui.results.detailed import render_detailed_breakdown
from ui.results.summary import render_summary
from ui.results.metrics import render_key_metrics_panel
from ui.results.dashboard import render_standard_dashboard
from ui.results.environmental import render_environmental_impact
from ui.results.live_preview import display_results_in_live_mode

__all__ = [
    'render_summary',
    'render_detailed_breakdown', 
    'render_charts',
    'display_results',
    'display_from_session_state',
    'render_key_metrics_panel',
    'render_standard_dashboard',
    'render_environmental_impact',
    'display_results_in_live_mode'
] 