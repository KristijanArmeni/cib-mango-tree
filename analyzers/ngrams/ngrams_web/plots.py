"""
Framework-agnostic Plotly figure builders for the n-grams analyzer.

These functions accept a Polars DataFrame and return a plain
``plotly.graph_objects.Figure``.  They have no dependency on Shiny,
Dash, or NiceGUI and can therefore be imported from any GUI layer.
"""

import numpy as np
import plotly.express as px
import polars as pl

from ..ngrams_base.interface import COL_NGRAM_ID, COL_NGRAM_LENGTH
from ..ngrams_stats.interface import (
    COL_NGRAM_DISTINCT_POSTER_COUNT,
    COL_NGRAM_TOTAL_REPS,
    COL_NGRAM_WORDS,
)


def plot_scatter(data: pl.DataFrame):
    """
    Build a log-log scatter plot of n-gram frequency vs. unique poster count.

    Each point represents one n-gram.  Points are coloured by n-gram length
    and carry ``customdata`` needed for click-based filtering:
    ``[words, ngram_id, total_reps]``.

    Args:
        data: The ``ngram_stats`` Polars DataFrame (must contain the standard
              n-gram statistics columns).

    Returns:
        A ``plotly.graph_objects.Figure`` ready to be passed to any Plotly
        renderer (``ui.plotly``, ``dcc.Graph``, ``fig.show()``, …).
    """
    rng = np.random.default_rng(seed=42)
    jitter_factor = 0.05

    data = data.with_columns(
        (
            pl.col(COL_NGRAM_TOTAL_REPS)
            * (1 + rng.uniform(-jitter_factor, jitter_factor, len(data)))
        ).alias("total_reps_jittered")
    )

    n_gram_categories = data.select(
        pl.col(COL_NGRAM_LENGTH).unique().sort()
    ).to_series()

    fig = px.scatter(
        data_frame=data,
        x=COL_NGRAM_DISTINCT_POSTER_COUNT,
        y="total_reps_jittered",
        log_y=True,
        log_x=True,
        custom_data=[COL_NGRAM_WORDS, COL_NGRAM_ID, COL_NGRAM_TOTAL_REPS],
        color=COL_NGRAM_LENGTH,
        category_orders={COL_NGRAM_LENGTH: n_gram_categories},
    )

    fig.update_traces(
        marker=dict(size=11, opacity=0.7, line=dict(width=0.5, color="white")),
        hovertemplate="<br>".join(
            [
                "<b>N-gram:</b> %{customdata[0]}",
                "<b>Frequency:</b> %{customdata[2]}",
                "<b>Nr. unique posters:</b> %{x}",
            ]
        ),
    )

    fig.update_layout(
        title_text="Repeated phrases and accounts",
        yaxis_title="N-gram frequency",
        xaxis_title="Nr. unique posters",
        hovermode="closest",
        legend=dict(title="N-gram length"),
        template="plotly_white",
    )

    return fig
