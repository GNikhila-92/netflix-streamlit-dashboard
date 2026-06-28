"""
app.py
Netflix Titles Dashboard — Premium dark-themed layout.
"""

import streamlit as st
import pandas as pd

from data_utils import (
    load_base_data,
    explode_genres,
    explode_countries,
    explode_cast,
    get_filter_options,
    apply_filters,
)
from charts import (
    titles_added_per_year_by_type,
    top_genres_bar,
    country_choropleth,
    ratings_distribution,
    month_year_heatmap,
    content_age_scatter,
)

st.set_page_config(
    page_title="Netflix Titles Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
    /* Full Dark Canvas Setup */
    .stApp {
        background-color: #141414 !important;
        color: #F5F5F1;
    }
    
    /* Sidebar Deep Dark Contrast Surface */
    section[data-testid="stSidebar"] {
        background-color: #0A0A0A !important;
        border-right: 1px solid #262626;
    }
    
    section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] span, section[data-testid="stSidebar"] label {
        color: #E2E8F0 !important;
    }
    
    h1, h2, h3, h4 {
        font-family: 'Helvetica Neue', Arial, sans-serif;
        color: #FFFFFF !important;
        font-weight: 700;
    }
    
    /* High Contrast Floating Container Cards */
    .metric-card {
        background: rgba(30, 30, 30, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 12px;
        padding: 22px;
        box-shadow: 0 10px 35px 0 rgba(0, 0, 0, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 16px;
    }
    
    /* Metrics Typography Configurations */
    .metric-val {
        font-size: 1.9rem;
        font-weight: 700;
        color: #E50914 !important; /* Netflix Red accent color */
        line-height: 1.2;
        margin-top: 4px;
    }
    .metric-lbl {
        font-size: 0.8rem;
        color: #A3A3A3 !important;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Dark Theme Tab Component Styling */
    div.stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(20, 20, 20, 0.8);
        padding: 6px 6px 0 6px;
        border-radius: 8px 8px 0 0;
        border-bottom: 2px solid #262626;
    }
    div.stTabs [data-baseweb="tab"] {
        background-color: #1F1F1F;
        border-radius: 6px 6px 0 0;
        padding: 10px 20px;
        color: #A3A3A3 !important; /* High contrast unselected tabs */
        font-weight: 600;
        border: 1px solid #262626;
        border-bottom: none;
    }
    div.stTabs [aria-selected="true"] {
        background-color: #E50914 !important; /* Active Tab Indicator */
        color: #FFFFFF !important;
        border-color: #E50914 !important;
    }
    
    /* High Contrast Grid Table Custom Formatting Override */
    div[data-testid="stDataFrame"] td, div[data-testid="stDataFrame"] th {
        color: #FFFFFF !important;
    }
    
    footer {visibility: hidden;}
    .custom-footer {
        margin-top: 40px;
        padding: 16px 0;
        text-align: center;
        color: #A3A3A3;
        border-top: 1px solid #262626;
        font-size: 0.85rem;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

st.markdown(
    "<h1 style='margin-bottom:0;'>Netflix Titles Dashboard</h1>"
    "<p style='color:#A3A3A3; margin-top:0; font-size:1.05rem; font-weight:500;'>"
    "Exploring 8,800+ titles — what Netflix added, when, and from where."
    "</p>",
    unsafe_allow_html=True,
)

DATA_PATH = "netflix_titles.csv"
try:
    base_df = load_base_data(DATA_PATH)
except FileNotFoundError:
    st.error(f"Could not find `{DATA_PATH}`. Place the CSV next to app.py and rerun.")
    st.stop()

filter_options = get_filter_options(base_df)

with st.sidebar:
    st.markdown("## Global Dashboard Filters")
    sel_types = st.multiselect("Type", filter_options["types"])
    sel_countries = st.multiselect("Country", filter_options["countries"])
    sel_genres = st.multiselect("Genre", filter_options["genres"])
    sel_ratings = st.multiselect("Rating", filter_options["ratings"])

    year_range = st.slider(
        "Release Year Range Selection",
        min_value=filter_options["year_min"],
        max_value=filter_options["year_max"],
        value=(filter_options["year_min"], filter_options["year_max"]),
    )

    if st.button("Reset Configuration Filters", use_container_width=True):
        st.rerun()

filtered_df = apply_filters(
    base_df, sel_types, sel_countries, sel_genres, sel_ratings, year_range
)

genres_long = explode_genres(filtered_df)
countries_long = explode_countries(filtered_df)
cast_long = explode_cast(filtered_df)

if filtered_df.empty:
    st.warning("No catalog rows track with the currently requested filtering parameters.")
    st.stop()

# Metric Aggregations
total_titles = len(filtered_df)
n_movies = (filtered_df["type"] == "Movie").sum()
n_tv = (filtered_df["type"] == "TV Show").sum()
n_countries = countries_long[countries_long["country_single"] != "Unknown"]["country_single"].nunique()
most_recent = filtered_df["date_added"].max()
avg_age = filtered_df["content_age_at_add"].mean()

# Render Metric Cards
k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    st.markdown(f'<div class="metric-card"><div class="metric-lbl">Total Record Footprint</div><div class="metric-val">{total_titles:,}</div></div>', unsafe_allow_html=True)
with k2:
    st.markdown(f'<div class="metric-card"><div class="metric-lbl">Movies / TV Shows</div><div class="metric-val" style="font-size:1.5rem;">{n_movies:,} / {n_tv:,}</div></div>', unsafe_allow_html=True)
with k3:
    st.markdown(f'<div class="metric-card"><div class="metric-lbl">Active Countries</div><div class="metric-val">{n_countries}</div></div>', unsafe_allow_html=True)
with k4:
    st.markdown(f'<div class="metric-card"><div class="metric-lbl">Latest Addition</div><div class="metric-val" style="font-size:1.35rem;">{most_recent.strftime("%b %d, %Y") if pd.notna(most_recent) else "N/A"}</div></div>', unsafe_allow_html=True)
with k5:
    st.markdown(f'<div class="metric-card"><div class="metric-lbl">Avg Catalog Age</div><div class="metric-val">{avg_age:.1f} yrs</div></div>', unsafe_allow_html=True)

# 4-Tab Deployment Architecture
tab_overview, tab_trends, tab_geo, tab_deep = st.tabs([
    "Overview Tracking", 
    "Dynamic Content Trends", 
    "Geography Performance", 
    "Resource Group Deep-Dive"
])

with tab_overview:
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(ratings_distribution(filtered_df), use_container_width=True)
    with c2:
        st.plotly_chart(top_genres_bar(genres_long), use_container_width=True)

    st.markdown("### Search Operational Data Archive")
    query = st.text_input("Search parameters line input", placeholder="e.g. 'love', 'dark', 'kitchen'", label_visibility="collapsed")
    table_df = filtered_df.copy()
    if query:
        table_df = table_df[table_df["title"].str.contains(query, case=False, na=False)]

    st.dataframe(
        table_df[["title", "type", "director", "country", "release_year", "rating", "duration", "listed_in", "description"]].sort_values("release_year", ascending=False),
        use_container_width=True,
        hide_index=True,
    )

with tab_trends:
    st.plotly_chart(titles_added_per_year_by_type(filtered_df), use_container_width=True)
    st.plotly_chart(month_year_heatmap(filtered_df), use_container_width=True)

with tab_geo:
    st.plotly_chart(country_choropleth(countries_long), use_container_width=True)
    top_countries = countries_long[countries_long["country_single"] != "Unknown"]["country_single"].value_counts().head(10).reset_index()
    top_countries.columns = ["Country", "Titles Managed"]
    st.dataframe(top_countries, hide_index=True, use_container_width=True)

with tab_deep:
    st.plotly_chart(content_age_scatter(filtered_df), use_container_width=True)
    lc1, lc2 = st.columns(2)
    with lc1:
        st.markdown("**Top 10 Active Directors**")
        top_directors = filtered_df[filtered_df["director"] != "Unknown"]["director"].value_counts().head(10).reset_index()
        top_directors.columns = ["Director", "Total Titles Output"]
        st.dataframe(top_directors, hide_index=True, use_container_width=True)
    with lc2:
        st.markdown("**Top 10 Featured Performance Actors**")
        top_actors = cast_long["actor"].value_counts().head(10).reset_index()
        top_actors.columns = ["Actor", "Total Project Castings"]
        st.dataframe(top_actors, hide_index=True, use_container_width=True)

st.markdown('<div class="custom-footer">Operational Dashboard Ecosystem · Powered by Streamlit</div>', unsafe_allow_html=True)
