import os
import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# STEP 1 - LOAD DATA
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "world_happiness_2023.csv")

df = pd.read_csv(DATA_PATH)

df.columns = df.columns.str.strip()

df = df.rename(columns={
    "Country name": "Country",
    "Regional indicator": "Region",
    "Ladder score": "Score",
    "Logged GDP per capita": "GDP",
    "Social support": "Social_Support",
    "Healthy life expectancy": "Life_Expectancy",
    "Freedom to make life choices": "Freedom",
    "Generosity": "Generosity",
    "Perceptions of corruption": "Corruption"
})

# --------------------------------------------------
# STEP 2 - PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="World Happiness Dashboard",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 World Happiness Dashboard")
st.caption("Source: World Happiness Report 2023")

# --------------------------------------------------
# STEP 3 - SIDEBAR FILTERS
# --------------------------------------------------

with st.sidebar:
    st.header("Filters")

    regions = ["All"] + sorted(df["Region"].unique().tolist())

    selected_region = st.selectbox(
        "Select Region",
        regions
    )

    top_n = st.slider(
        "Show Top N Countries",
        min_value=5,
        max_value=25,
        value=15
    )

filtered = (
    df if selected_region == "All"
    else df[df["Region"] == selected_region]
)

# --------------------------------------------------
# STEP 4 - KPI METRICS
# --------------------------------------------------

col1, col2, col3 = st.columns(3)

col1.metric(
    "Countries",
    len(filtered)
)

col2.metric(
    "Average Score",
    f"{filtered['Score'].mean():.2f}"
)

col3.metric(
    "Happiest Country",
    filtered.loc[
        filtered["Score"].idxmax(),
        "Country"
    ]
)

st.divider()

# --------------------------------------------------
# STEP 5 - MAIN DASHBOARD CHARTS
# --------------------------------------------------

left_col, right_col = st.columns(2)

# ---------- Chart 1 ----------
with left_col:

    st.subheader("Top Happiness Rankings")

    top = (
        filtered
        .nlargest(top_n, "Score")
        .sort_values("Score")
    )

    fig1 = px.bar(
        top,
        x="Score",
        y="Country",
        orientation="h",
        color="Score",
        color_continuous_scale="Blues"
    )

    fig1.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        coloraxis_showscale=False
    )

    st.plotly_chart(
        fig1,
        use_container_width=True
    )

# ---------- Chart 2 ----------
with right_col:

    st.subheader("GDP vs Happiness")

    fig2 = px.scatter(
        filtered,
        x="GDP",
        y="Score",
        color="Region",
        hover_name="Country"
    )

    fig2.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

st.divider()

# --------------------------------------------------
# STEP 6 - DIVERGING CHART
# --------------------------------------------------

st.subheader("Freedom to Make Life Choices")

midpoint = df["Freedom"].mean()

fig3 = px.bar(
    filtered.sort_values("Freedom"),
    x="Freedom",
    y="Country",
    orientation="h",
    color="Freedom",
    color_continuous_scale="RdBu",
    color_continuous_midpoint=midpoint
)

fig3.add_vline(
    x=midpoint,
    line_width=2,
    line_dash="dash"
)

fig3.add_annotation(
    x=midpoint,
    y=0,
    text="Global Average",
    showarrow=False
)

fig3.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white"
)

st.plotly_chart(
    fig3,
    use_container_width=True
)

st.divider()
st.caption("Built with Streamlit + Plotly")