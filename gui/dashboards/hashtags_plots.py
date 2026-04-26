"""
Framework-agnostic ECharts figure builders for the hashtags analyzer.

These functions accept Polars DataFrames and return ECharts option dicts.
They have no dependency on Shiny, Dash, or NiceGUI.
"""

from datetime import datetime

import polars as pl

from analyzers.hashtags.hashtags_base.interface import (
    OUTPUT_COL_GINI,
    OUTPUT_COL_HASHTAGS,
    OUTPUT_COL_TIMESPAN,
    OUTPUT_COL_USERS,
)

MANGO_DARK_GREEN = "#609949"
MANGO_DARK_ORANGE = "#f3921e"
LIGHT_BLUE = "#acd7e5"


def _format_date_for_axis(ts: datetime, is_hourly: bool) -> str:
    """Format datetime for x-axis labels based on bin size."""
    if is_hourly:
        return ts.strftime("%b %d, %Y %H:%M")
    return ts.strftime("%b %d, %Y")


def _detect_is_hourly(df: pl.DataFrame) -> bool:
    """Detect if the time bins are hourly (or smaller) vs daily."""
    if len(df) < 2:
        return False
    time_step = df[OUTPUT_COL_TIMESPAN][1] - df[OUTPUT_COL_TIMESPAN][0]
    return time_step.total_seconds() < 86400  # less than 1 day


def plot_gini_echart(
    df: pl.DataFrame,
    smooth: bool = False,
) -> dict:
    """
    Build a line chart of Gini coefficient over time.

    Args:
        df: Primary output DataFrame with 'timewindow_start' and 'gini' columns.
        smooth: Whether to include a smoothed line (requires 'gini_smooth' column).

    Returns:
        ECharts option dict ready for ui.echart().
    """
    is_hourly = _detect_is_hourly(df)
    x_values = [
        _format_date_for_axis(ts, is_hourly) for ts in df[OUTPUT_COL_TIMESPAN].to_list()
    ]
    y_values = df[OUTPUT_COL_GINI].to_list()

    # Dynamic interval to show ~8-10 labels on x-axis
    n_points = len(x_values)
    interval = max(0, n_points // 9) if n_points > 10 else 0

    # Build series data with both display label and machine-readable timestamp
    series_data = [
        {
            "value": [display_ts, gini],
            "raw_ts": ts.strftime("%Y-%m-%d %H:%M"),
        }
        for ts, display_ts, gini in zip(
            df[OUTPUT_COL_TIMESPAN].to_list(), x_values, y_values
        )
    ]

    series = [
        {
            "name": "Gini coefficient",
            "type": "line",
            "data": series_data,
            "lineStyle": {"color": "black", "width": 1.5},
            "showSymbol": False,
            "symbol": "circle",
            "symbolSize": 4,
            "itemStyle": {"color": "black"},
            "emphasis": {
                "showSymbol": True,
                "itemStyle": {
                    "color": "#d62728",
                    "symbolSize": 12,
                    "shadowBlur": 10,
                    "shadowColor": "rgba(0, 0, 0, 0.3)",
                },
            },
        }
    ]

    if smooth and "gini_smooth" in df.columns:
        y_smooth = df["gini_smooth"].to_list()
        smooth_series_data = [
            {
                "value": [display_ts, gini_s],
                "raw_ts": ts.strftime("%Y-%m-%d %H:%M"),
            }
            for ts, display_ts, gini_s in zip(
                df[OUTPUT_COL_TIMESPAN].to_list(), x_values, y_smooth
            )
        ]
        series.append(
            {
                "name": "Smoothed",
                "type": "line",
                "data": smooth_series_data,
                "lineStyle": {"color": MANGO_DARK_ORANGE, "width": 2},
                "itemStyle": {"color": MANGO_DARK_ORANGE},
                "showSymbol": False,
                "emphasis": {
                    "showSymbol": True,
                    "itemStyle": {
                        "color": "#d62728",
                        "symbolSize": 12,
                        "shadowBlur": 10,
                        "shadowColor": "rgba(0, 0, 0, 0.3)",
                    },
                },
            }
        )

    return {
        "title": {"text": "Concentration of hashtags over time"},
        "tooltip": {
            "trigger": "axis",
            "axisPointer": {"type": "cross"},
            ":formatter": """function(params) {
                if (!params || params.length === 0) return '';
                var p = params[0];
                var html = '<b>' + p.axisValue + '</b><br/>';
                for (var i = 0; i < params.length; i++) {
                    html += params[i].marker + params[i].seriesName + ': '
                          + params[i].value[1].toFixed(3) + '<br/>';
                }
                return html;
            }""",
        },
        "grid": {"left": 60, "right": 30, "top": 50, "bottom": 50},
        "xAxis": {
            "type": "category",
            "data": x_values,
            "name": "Time window (start date)",
            "nameLocation": "middle",
            "nameGap": 30,
            "nameTextStyle": {"fontSize": 13},
            "axisLabel": {
                "fontSize": 11,
                "interval": interval,
            },
        },
        "yAxis": {
            "type": "value",
            "name": "Hashtag Concentration\n(Gini coefficient)",
            "nameLocation": "middle",
            "nameGap": 50,
            "nameTextStyle": {"fontSize": 13},
            "min": 0,
            "max": 1,
            "axisLabel": {
                ":formatter": "function(value) { return value.toFixed(2); }",
                "fontSize": 11,
            },
        },
        "series": series,
    }


def plot_hashtag_bar_echart(
    df_secondary: pl.DataFrame,
    selected_date: datetime | None = None,
) -> dict:
    """
    Build a horizontal bar chart of hashtag frequency for a selected time window.

    Args:
        df_secondary: Output of secondary_analyzer() with 'hashtags' and
                      'hashtag_perc' columns, sorted by hashtag_perc.
        selected_date: The selected timewindow start (for title).

    Returns:
        ECharts option dict. Empty placeholder if df is empty.
    """
    if df_secondary.is_empty():
        return {
            "option": _empty_placeholder("No data for selected date"),
            "height": 300,
        }

    df_sorted = df_secondary.sort("hashtag_perc", descending=False)
    hashtags = df_sorted[OUTPUT_COL_HASHTAGS].to_list()
    percentages = df_sorted["hashtag_perc"].to_list()

    max_pct = max(percentages) if percentages else 1

    if selected_date:
        title = f"Most frequent hashtags — {selected_date.strftime('%B %d, %Y')}"
    else:
        title = "Most frequent hashtags"

    series_data = [
        {
            "value": pct,
            "name": tag,
        }
        for tag, pct in zip(hashtags, percentages)
    ]

    bar_height = max(30, len(hashtags) * 30 + 100)

    return {
        "option": {
            "title": {"text": title},
            "tooltip": {
                "trigger": "axis",
                "axisPointer": {"type": "shadow"},
                ":formatter": """function(params) {
                    var p = params[0];
                    return '<b>' + p.name + '</b><br/>'
                         + p.value.toFixed(1) + '% of all hashtags';
                }""",
            },
            "grid": {"left": 10, "right": 60, "top": 40, "bottom": 40},
            "xAxis": {
                "type": "value",
                "name": "% all hashtags in the selected time window",
                "nameLocation": "end",
                "nameGap": 10,
                "nameTextStyle": {"fontSize": 12, "align": "left"},
                "max": max_pct * 1.5,
                "position": "top",
                "axisLabel": {"fontSize": 11},
            },
            "yAxis": {
                "type": "category",
                "data": hashtags,
                "show": False,
            },
            "series": [
                {
                    "type": "bar",
                    "data": series_data,
                    "itemStyle": {"color": MANGO_DARK_GREEN},
                    "barWidth": 24,
                    "label": {
                        "show": True,
                        "position": "right",
                        "formatter": "{b}",
                        "fontSize": 12,
                        "color": "black",
                    },
                }
            ],
        },
        "height": bar_height,
    }


def plot_users_bar_echart(users_data: pl.DataFrame) -> dict:
    """
    Build a horizontal bar chart showing hashtag usage per user.

    Args:
        users_data: DataFrame with 'users_all' and 'count' columns.

    Returns:
        ECharts option dict with 'option' and 'height' keys.
        Empty placeholder if no users.
    """
    if users_data.is_empty():
        return {
            "option": _empty_placeholder("No users found for this hashtag"),
            "height": 300,
        }

    df_sorted = users_data.sort("count", descending=False)
    users = df_sorted["users_all"].to_list()
    counts = df_sorted["count"].to_list()

    max_count = max(counts) if counts else 1
    bar_height = max(30, len(users) * 30 + 100)

    series_data = [
        {
            "value": cnt,
            "name": user,
        }
        for user, cnt in zip(users, counts)
    ]

    return {
        "option": {
            "tooltip": {
                "trigger": "axis",
                "axisPointer": {"type": "shadow"},
                ":formatter": """function(params) {
                    var p = params[0];
                    return '<b>' + p.name + '</b><br/>'
                         + p.value + ' posts';
                }""",
            },
            "grid": {"left": 10, "right": 60, "top": 10, "bottom": 10},
            "xAxis": {
                "type": "value",
                "name": "Number of posts",
                "nameLocation": "end",
                "nameGap": 10,
                "nameTextStyle": {"fontSize": 12, "align": "left"},
                "max": max_count * 1.5,
                "position": "top",
                "axisLabel": {"fontSize": 11},
            },
            "yAxis": {
                "type": "category",
                "data": users,
                "show": False,
            },
            "series": [
                {
                    "type": "bar",
                    "data": series_data,
                    "itemStyle": {"color": MANGO_DARK_GREEN},
                    "barWidth": 24,
                    "label": {
                        "show": True,
                        "position": "right",
                        "formatter": "{b}",
                        "fontSize": 12,
                        "color": "black",
                    },
                }
            ],
        },
        "height": bar_height,
    }


def _empty_placeholder(message: str) -> dict:
    """Create an empty ECharts option with a centered text message."""
    return {
        "title": {
            "text": message,
            "left": "center",
            "top": "middle",
            "textStyle": {"fontSize": 16, "color": "#999"},
        },
        "xAxis": {"show": False},
        "yAxis": {"show": False},
        "series": [],
        "grid": {"left": 0, "right": 0, "top": 0, "bottom": 0},
    }
