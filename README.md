# Netflix Titles Dashboard

An interactive, premium dark-themed web application built with Streamlit and Plotly to analyze over 8,800 Netflix movies and TV shows. This dashboard tracks content additions, catalog age gaps, genres, ratings, and global production distributions.

## Live Application

The dashboard is deployed live on the web and updates automatically. You can access the live system here:
👉 **[Live Netflix Titles Dashboard Deployment](https://share.streamlit.io/GNikhila-92/netflix-streamlit-dashboard/main/app.py)**

## Interface Preview

<p align="center">
  <img src="dashboard_preview.png" alt="Netflix Titles Dashboard Interface Preview" width="100%">
</p>

## Interactive Features

* **Overview Tracking Tab:** Displays high-level KPIs (Total Footprint, Movie vs TV Show splits, Active Countries) alongside content ratings distribution, top-performing genres, and a fully searchable operational data archive table.
* **Dynamic Content Trends Tab:** Features area timelines tracking historical content drop frequencies per year and a month-vs-year release drop heatmap matrix.
* **Geography Performance Tab:** Provides an interactive global choropleth map plotting total catalog contributions by country alongside a top 10 producers list data table.
* **Resource Group Deep-Dive Tab:** Includes scatter plots tracking content acquisition delays over time alongside automated ranking lists for the top 10 active directors and featured actors.
* **Global Sidebar Filters:** Allows dynamic multi-value filtering by Type, Country, Genre, Rating, and Release Year Range that automatically recalculates every chart and card on the dashboard simultaneously.

## Tech Stack

* **Frontend Framework:** Streamlit (Python)
* **Data Processing & Analytics:** Pandas, NumPy
* **Data Visualization:** Plotly Express, Plotly Graph Objects
* **Styling Integration:** Custom CSS injections for floating card containers and structured typography contrast.
