"""
Base class for all analyzer dashboard pages.

Provides a standard layout shell for dashboards:
- Header inherited from GuiPage (with back-to-results navigation)
- A full-width content area for charts and tables
- Footer inherited from GuiPage

All analyzer-specific dashboard pages should subclass BaseDashboardPage
and implement render_content().
"""

import abc

from gui.base import GuiPage, GuiSession, gui_routes


class BaseDashboardPage(GuiPage, abc.ABC):
    """
    Abstract base class for all analyzer dashboard pages.

    Extends GuiPage with dashboard-specific defaults:
    - Back button navigates to the post-analysis page
    - Title is derived from the selected analyzer name
    - Footer is shown

    Subclasses implement render_content() to provide the actual
    charts, tables, and interactive controls for each analyzer.

    Usage:
        ```python
        class NgramsDashboardPage(BaseDashboardPage):
            def render_content(self) -> None:
                ui.label("N-grams dashboard content here")
        ```
    """

    def __init__(self, session: GuiSession):
        analyzer_name = (
            session.selected_analyzer_name
            if session.selected_analyzer_name
            else "Results Dashboard"
        )
        super().__init__(
            session=session,
            route=gui_routes.dashboard,
            title=f"{analyzer_name}: Results Dashboard",
            show_back_button=True,
            back_route=gui_routes.post_analysis,
            show_footer=True,
        )

    @abc.abstractmethod
    def render_content(self) -> None:
        """Render dashboard-specific charts, tables, and controls."""
        raise NotImplementedError
