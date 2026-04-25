"""
Hashtags analyzer dashboard page (minimal).

Displays the Gini coefficient line plot over time.
Additional panels and interactivity will be added incrementally.
"""

import polars as pl
from nicegui import run, ui

from gui.dashboards.hashtags_data import load_primary_output
from gui.session import GuiSession

from .base_dashboard import BaseDashboardPage
from .hashtags_plots import plot_gini_echart


class HashtagsDashboardPage(BaseDashboardPage):
    """
    Minimal results dashboard for the Hashtags analyzer.

    Renders a Gini coefficient line plot over time.
    """

    def __init__(self, session: GuiSession):
        super().__init__(session=session)
        self._df_primary: pl.DataFrame | None = None
        self._smooth: bool = False
        self._gini_chart: ui.echart | None = None
        self._gini_loading: ui.column | None = None
        self._gini_content: ui.column | None = None
        self._smooth_checkbox: ui.checkbox | None = None

    async def _load_and_render_async(self) -> None:
        try:
            self._df_primary = await run.io_bound(load_primary_output, self.session)
        except Exception as exc:
            if self._gini_loading is not None:
                self._show_error(
                    self._gini_loading, f"Could not load hashtag analysis: {exc}"
                )
            return

        if self._df_primary.is_empty():
            if self._gini_loading is not None:
                self._show_error(self._gini_loading, "No hashtag data available.")
            return

        try:
            option = await run.cpu_bound(
                plot_gini_echart,
                self._df_primary,
                self._smooth,
            )
        except Exception as exc:
            if self._gini_loading is not None:
                self._show_error(self._gini_loading, f"Could not build chart: {exc}")
            return

        if (
            self._gini_chart is None
            or self._gini_content is None
            or self._gini_loading is None
        ):
            return

        self._gini_chart.options.update(option)
        self._gini_chart.update()
        self._show_content(self._gini_loading, self._gini_content)

    def _handle_smooth_change(self, e) -> None:
        self._smooth = e.value
        if self._gini_chart is not None and self._df_primary is not None:
            option = plot_gini_echart(self._df_primary, smooth=self._smooth)
            self._gini_chart.options.update(option)
            self._gini_chart.update()

    def render_content(self) -> None:
        """Render the Gini line plot with loading state."""
        with ui.row().classes("w-full justify-center"):
            with ui.column().classes("w-3/4 q-pa-md gap-4"):
                with ui.card().classes("w-full"):
                    with ui.row().classes("w-full items-center"):
                        self._smooth_checkbox = ui.checkbox(
                            "Show smoothed line",
                            value=False,
                            on_change=self._handle_smooth_change,
                        )
                    self._gini_loading, self._gini_content = (
                        self._create_loading_container("350px")
                    )
                    with self._gini_content:
                        self._gini_chart = (
                            ui.echart({}).classes("w-full").style("height: 350px")
                        )

        ui.timer(0, self._load_and_render_async, once=True)
