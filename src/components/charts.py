"""
Plotly Chart visualizers for Dashboards and Analytics views.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st


def render_category_pie_chart(category_counts: dict, title: str = "Donations by Category"):
    """Renders a modern doughnut chart for category breakdown."""
    if not category_counts or sum(category_counts.values()) == 0:
        st.info("No category data available yet.")
        return

    df = pd.DataFrame(
        list(category_counts.items()),
        columns=["Category", "Count"],
    )
    
    fig = px.pie(
        df,
        values="Count",
        names="Category",
        hole=0.55,
        color_discrete_sequence=px.colors.qualitative.Prism,
    )
    fig.update_layout(
        title={"text": title, "font": {"size": 16, "color": "#f8fafc"}},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend={"font": {"color": "#cbd5e1"}},
        margin=dict(t=40, b=20, l=20, r=20),
        height=300,
    )
    st.plotly_chart(fig, use_container_width=True)


def render_status_bar_chart(status_counts: dict, title: str = "Donation Status Breakdown"):
    """Renders a modern horizontal bar chart for status progress."""
    if not status_counts or sum(status_counts.values()) == 0:
        st.info("No status data available yet.")
        return

    df = pd.DataFrame(
        list(status_counts.items()),
        columns=["Status", "Count"],
    )

    color_map = {
        "Pending": "#f59e0b",
        "Accepted": "#10b981",
        "Rejected": "#ef4444",
        "Collected": "#8b5cf6",
        "Confirmed": "#3b82f6",
        "Dispatched": "#06b6d4",
        "Delivered": "#10b981",
    }
    colors = [color_map.get(s, "#38bdf8") for s in df["Status"]]

    fig = go.Figure(
        go.Bar(
            x=df["Count"],
            y=df["Status"],
            orientation="h",
            marker=dict(color=colors, line=dict(width=0)),
            text=df["Count"],
            textposition="auto",
        )
    )
    fig.update_layout(
        title={"text": title, "font": {"size": 16, "color": "#f8fafc"}},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=True, gridcolor="rgba(148, 163, 184, 0.1)", tickfont=dict(color="#94a3b8")),
        yaxis=dict(tickfont=dict(color="#f8fafc")),
        margin=dict(t=40, b=20, l=20, r=20),
        height=280,
    )
    st.plotly_chart(fig, use_container_width=True)


def render_timeline_chart(monthly_data: dict, title: str = "Monthly Contribution Trend"):
    """Renders an interactive line area chart for activity trend."""
    if not monthly_data:
        st.info("No timeline data available.")
        return

    df = pd.DataFrame(
        list(monthly_data.items()),
        columns=["Month", "Contributions"],
    )
    fig = px.area(
        df,
        x="Month",
        y="Contributions",
        color_discrete_sequence=["#8b5cf6"],
    )
    fig.update_layout(
        title={"text": title, "font": {"size": 16, "color": "#f8fafc"}},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(gridcolor="rgba(148, 163, 184, 0.1)", tickfont=dict(color="#94a3b8")),
        yaxis=dict(gridcolor="rgba(148, 163, 184, 0.1)", tickfont=dict(color="#94a3b8")),
        margin=dict(t=40, b=20, l=20, r=20),
        height=280,
    )
    st.plotly_chart(fig, use_container_width=True)
