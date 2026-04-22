"""
Dashboard pages for the NiceGUI GUI.

Each analyzer that produces results has a corresponding dashboard module here.
All dashboard pages inherit from BaseDashboardPage, which extends GuiPage.

Modules:
    base_dashboard: BaseDashboardPage abstract base class
    ngrams: NgramsDashboardPage for the n-grams analyzer
    placeholder: PlaceholderDashboard shown when no dashboard exists yet
    hashtags: HashtagsDashboardPage for the hashtags analyzer  (planned)
    temporal: TemporalDashboardPage for the temporal analyzer  (planned)
"""

from .base_dashboard import BaseDashboardPage
from .ngrams import NgramsDashboardPage
from .placeholder import PlaceholderDashboard

# Maps primary analyzer IDs to their dashboard page classes.
# Add an entry here when a new dashboard is implemented.
_DASHBOARD_REGISTRY: dict[str, type[BaseDashboardPage]] = {
    "ngrams": NgramsDashboardPage,
}


def get_dashboard(analyzer_id: str | None) -> type[BaseDashboardPage] | None:
    """Look up a registered dashboard class by analyzer ID."""
    return _DASHBOARD_REGISTRY.get(analyzer_id) if analyzer_id else None


__all__ = [
    "BaseDashboardPage",
    "NgramsDashboardPage",
    "PlaceholderDashboard",
    "get_dashboard",
]
