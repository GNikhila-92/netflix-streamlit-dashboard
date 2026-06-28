"""
charts.py
All Plotly figure-builder functions for the premium dark-themed Netflix dashboard.
Ensures high contrast visibility against pure dark canvases.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

COLOR_TEXT = "#F5F5F1"       # Light gray text for high readability on black canvas
COLOR_MUTED = "#A3A3A3"      # Muted labels gray
COLOR_GRID = "#262626"       # Subtle border grid tint lines

# Vivid theme colors for dark canvas visualization stability
PALETTE_TRENDS = ["#E50914", "#F5F5F1"]   # Netflix Red / Clean Off-White
PALETTE_RATINGS = ["#B81D24", "#404040"]  # Medium Crimson / Charcoal Gray
PALETTE_SCATTER = ["#E50914", "#38BDF8"]  # Red / Electric Sky Blue

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=COLOR_TEXT, family="Helvetica Neue, Arial, sans-serif"),
    margin=dict(l=10, r=10, t=50, b=10),
    legend=dict(bgcolor="rgba(20,20,20,0.8)", font=dict(color=COLOR_TEXT, size=11)),
)


def _style(fig: go.Figure, title: str = None) -> go.Figure:
    fig.update_layout(**PLOTLY_LAYOUT)
    if title:
        fig.update_layout(title=dict(text=title, font=dict(size=16, color=COLOR_TEXT, family="Helvetica Neue, Arial, sans-serif")))
    
    # Overriding layout inheritance tracking boundaries
    fig.update_xaxes(
        showgrid=False, 
        zeroline=False, 
        title_font=dict(color=COLOR_TEXT, size=13),
        tickfont=dict(color=COLOR_MUTED, size=11, inherit=False)
    )
    fig.update_yaxes(
        showgrid=True, 
        gridcolor=COLOR_GRID, 
        zeroline=False, 
        title_font=dict(color=COLOR_TEXT, size=13),
        tickfont=dict(color=COLOR_MUTED, size=11, inherit=False)
    )
    
    fig.update_layout(
        legend=dict(
            font=dict(color=COLOR_TEXT, size=11),
            title=dict(font=dict(color=COLOR_TEXT, size=11))
        )
    )
    return fig


def titles_added_per_year_by_type(df: pd.DataFrame) -> go.Figure:
    """Stacked area chart: count of titles added per year, split by Type."""
    data = (
        df.dropna(subset=["year_added"])
        .groupby(["year_added", "type"])
        .size()
        .reset_index(name="count")
    )
    data["year_added"] = data["year_added"].astype(int)
    fig = px.area(
        data, x="year_added", y="count", color="type",
        color_discrete_sequence=PALETTE_TRENDS,
        labels={"year_added": "Year Added", "count": "Titles Added", "type": "Type"},
    )
    fig.update_traces(line=dict(width=3, shape="spline"))
    return _style(fig, "Titles Added Per Year by Type")


def top_genres_bar(genres_long: pd.DataFrame, top_n: int = 10) -> go.Figure:
    """Horizontal bar chart of the top N genres by title count."""
    data = (
        genres_long["genre"].value_counts().head(top_n).reset_index()
    )
    data.columns = ["genre", "count"]
    fig = px.bar(
        data.sort_values("count"), x="count", y="genre", orientation="h",
        color="count", color_continuous_scale=["#404040", "#E50914"],
        labels={"count": "Number of Titles", "genre": "Genre"},
    )
    fig.update_layout(coloraxis_showscale=False, showlegend=False)
    fig.update_yaxes(showgrid=False)
    return _style(fig, "Top Genres Distribution")


def country_choropleth(countries_long: pd.DataFrame) -> go.Figure:
    """Choropleth map of title counts by country."""
    data = (
        countries_long[countries_long["country_single"] != "Unknown"]
        .groupby("country_single")
        .size()
        .reset_index(name="count")
    )
    fig = px.choropleth(
        data, locations="country_single", locationmode="country names",
        color="count", color_continuous_scale=["#171717", "#B81D24", "#E50914"],
        labels={"count": "Titles", "country_single": "Country"},
    )
    fig.update_geos(
        bgcolor="rgba(0,0,0,0)",
        showframe=False,
        showcoastlines=True,
        coastlinecolor="#404040",
        landcolor="#171717",
    )
    fig.update_layout(coloraxis_colorbar=dict(title="Titles Total", titlefont=dict(color=COLOR_TEXT), tickfont=dict(color=COLOR_MUTED)))
    return _style(fig, "Global Distribution Model")


def ratings_distribution(df: pd.DataFrame) -> go.Figure:
    """Grouped bar chart of rating distribution split by Movie/TV Show."""
    data = (
        df.groupby(["rating", "type"]).size().reset_index(name="count")
    )
    order = (
        df["rating"].value_counts().index.tolist()
    )
    fig = px.bar(
        data, x="rating", y="count", color="type", barmode="group",
        category_orders={"rating": order},
        color_discrete_sequence=PALETTE_RATINGS,
        labels={"rating": "Rating Category", "count": "Titles Volume", "type": "Type"},
    )
    return _style(fig, "Ratings Distribution Breakdown")


def month_year_heatmap(df: pd.DataFrame) -> go.Figure:
    """Heatmap of titles added: month (x) vs year (y)."""
    data = (
        df.dropna(subset=["year_added", "month_added"])
        .groupby(["year_added", "month_added"])
        .size()
        .reset_index(name="count")
    )
    pivot = data.pivot(index="year_added", columns="month_added", values="count").fillna(0)
    month_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    pivot = pivot.reindex(columns=range(1, 13))
    fig = go.Figure(
        data=go.Heatmap(
            z=pivot.values,
            x=month_labels,
            y=pivot.index.astype(int),
            colorscale=[[0, "#171717"], [0.5, "#B81D24"], [1, "#E50914"]],
            colorbar=dict(title="Volume Scale", titlefont=dict(color=COLOR_TEXT), tickfont=dict(color=COLOR_MUTED)),
            hovertemplate="Year: %{y}<br>Month: %{x}<br>Titles added: %{z}<extra></extra>",
        )
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)
    return _style(fig, "Content Drop Heatmap Matrix")


def content_age_scatter(df: pd.DataFrame) -> go.Figure:
    """Scatter: release_year vs content_age_at_add."""
    data = df.dropna(subset=["release_year", "content_age_at_add"])
    fig = px.scatter(
        data, x="release_year", y="content_age_at_add", color="type",
        color_discrete_sequence=PALETTE_SCATTER,
        opacity=0.75,
        labels={
            "release_year": "Original Release Year",
            "content_age_at_add": "Years Delay Until Added",
            "type": "Type",
        },
        hover_data={"title": True} if "title" in data.columns else None,
    )
    fig.update_traces(marker=dict(size=7))
    return _style(fig, "Content Acquisition Timeline Metrics")
