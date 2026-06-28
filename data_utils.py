"""
data_utils.py
Data loading, cleaning, and transformation utilities for the Netflix dashboard.

Design notes:
- Two cached frames are produced: a "base" cleaned frame (one row per title,
  used for KPIs / counts that must not be inflated by exploding) and an
  "exploded" long-form frame (one row per title x country x genre x cast
  member, used for groupby/aggregation charts like top genres or the
  choropleth). Keeping both avoids double-counting titles in KPIs while
  still allowing accurate multi-value aggregation.
"""

import numpy as np
import pandas as pd
import streamlit as st
import re

RAW_COLUMNS = [
    "show_id", "type", "title", "director", "cast", "country",
    "date_added", "release_year", "rating", "duration", "listed_in",
    "description",
]


@st.cache_data(show_spinner="Loading and cleaning Netflix data...")
def load_base_data(path: str = "netflix_titles.csv") -> pd.DataFrame:
    """Load the raw CSV and apply all single-row cleaning steps.

    Returns one row per title (no explosion of multi-value columns).
    """
    df = pd.read_csv(path)

    # --- Fill missing categorical fields rather than dropping rows ---
    df["director"] = df["director"].fillna("Unknown")
    df["country"] = df["country"].fillna("Unknown")
    df["cast"] = df["cast"].fillna("Unknown")
    df["listed_in"] = df["listed_in"].fillna("Unknown")
    df["rating"] = df["rating"].fillna("Not Rated")

    # --- Parse date_added into real datetime ---
    df["date_added"] = pd.to_datetime(df["date_added"].str.strip(), errors="coerce")
    df["year_added"] = df["date_added"].dt.year
    df["month_added"] = df["date_added"].dt.month
    df["month_name_added"] = df["date_added"].dt.month_name()

    # --- Split duration into duration_minutes (Movie) / seasons (TV Show) ---
    duration_num = df["duration"].str.extract(r"(\d+)").astype(float)[0]
    is_movie = df["type"] == "Movie"
    df["duration_minutes"] = np.where(is_movie, duration_num, np.nan)
    df["seasons"] = np.where(~is_movie, duration_num, np.nan)

    # --- Convenience fields used across charts/KPIs ---
    df["primary_country"] = (
        df["country"].str.split(",").str[0].str.strip().replace("", "Unknown")
    )
    df["content_age_at_add"] = df["year_added"] - df["release_year"]
    # Negative ages (data entry artifacts: added before release) clipped to 0
    df["content_age_at_add"] = df["content_age_at_add"].clip(lower=0)

    df["release_year"] = df["release_year"].astype("Int64")

    return df


def _explode_column(df: pd.DataFrame, col: str, new_col: str) -> pd.DataFrame:
    """Split a comma-separated string column into one row per value."""
    out = df.copy()
    out[new_col] = out[col].str.split(",")
    out = out.explode(new_col)
    out[new_col] = out[new_col].str.strip()
    out = out[out[new_col].ne("")]
    return out


@st.cache_data(show_spinner=False)
def explode_genres(df: pd.DataFrame) -> pd.DataFrame:
    return _explode_column(df, "listed_in", "genre")


@st.cache_data(show_spinner=False)
def explode_countries(df: pd.DataFrame) -> pd.DataFrame:
    return _explode_column(df, "country", "country_single")


@st.cache_data(show_spinner=False)
def explode_cast(df: pd.DataFrame) -> pd.DataFrame:
    out = _explode_column(df, "cast", "actor")
    return out[out["actor"] != "Unknown"]


@st.cache_data(show_spinner=False)
def get_filter_options(df: pd.DataFrame) -> dict:
    """Precompute sidebar filter option lists once per base-data load."""
    genres_long = explode_genres(df)
    countries_long = explode_countries(df)
    return {
        "types": sorted(df["type"].dropna().unique().tolist()),
        "countries": sorted(
            c for c in countries_long["country_single"].unique() if c
        ),
        "genres": sorted(g for g in genres_long["genre"].unique() if g),
        "ratings": sorted(df["rating"].dropna().unique().tolist()),
        "year_min": int(df["release_year"].dropna().min()),
        "year_max": int(df["release_year"].dropna().max()),
    }


def apply_filters(
    df: pd.DataFrame,
    types: list,
    countries: list,
    genres: list,
    ratings: list,
    year_range: tuple,
) -> pd.DataFrame:
    """Apply all sidebar filters to the base (non-exploded) frame.

    Country/genre filtering uses substring containment so a title with
    "United States, France" still matches a "United States" filter without
    needing to explode the base frame (which would inflate KPI counts).
    """
    out = df.copy()

    if types:
        out = out[out["type"].isin(types)]

    if countries:
        pattern = "|".join(re.escape(c) for c in countries)
        out = out[out["country"].str.contains(pattern, case=False, na=False)]

    if genres:
        pattern = "|".join(re.escape(g) for g in genres)
        out = out[out["listed_in"].str.contains(pattern, case=False, na=False)]

    if ratings:
        out = out[out["rating"].isin(ratings)]

    out = out[
        out["release_year"].between(year_range[0], year_range[1], inclusive="both")
        | out["release_year"].isna()
    ]
    return out
