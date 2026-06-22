import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import datetime

# ─────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="CO2 Dashboard",
    page_icon="🌱",
    layout="wide"
)


# ─────────────────────────────────────────────
# Load data
# ─────────────────────────────────────────────
@st.cache_data
def load_data():

    path = Path(__file__).parent / "co2_emissions.csv"

    df = pd.read_csv(path)

    df["Date"] = pd.to_datetime(
        df["Year"].astype(str) + "-01-01"
    )

    return df


df = load_data()


# ─────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────
st.title("🌱 CO2 Emissions Explorer")
st.caption(
    "Source: Our World in Data — ourworldindata.org/co2-emissions"
)


# ─────────────────────────────────────────────
# Sidebar filters
# ─────────────────────────────────────────────
with st.sidebar:

    st.header("Filters")


    # Region selectbox
    regions = ["All"] + sorted(
        df["Region"].dropna().unique()
    )

    selected_region = st.selectbox(
        "Region",
        regions
    )


    # Country multiselect chained to region
    if selected_region == "All":

        country_options = sorted(
            df["Country"].dropna().unique()
        )

    else:

        country_options = sorted(
            df[
                df["Region"] == selected_region
            ]["Country"]
            .dropna()
            .unique()
        )


    selected_countries = st.multiselect(
        "Countries",
        country_options,
        default=country_options[:5]
    )


    # Year range
    year_range = st.slider(
        "Year range",

        int(df["Year"].min()),
        int(df["Year"].max()),

        (
            int(df["Year"].min()),
            int(df["Year"].max())
        )
    )


    metric = st.radio(
        "Metric",
        [
            "Total CO2 (Mt)",
            "CO2 per capita"
        ]
    )


    highlight_top = st.checkbox(
        "Show only top emitter highlighted"
    )



# ─────────────────────────────────────────────
# Guards
# ─────────────────────────────────────────────

if not selected_countries:

    st.warning(
        "👆 Select at least one country."
    )

    st.stop()



# ─────────────────────────────────────────────
# Filtering
# ─────────────────────────────────────────────

filtered = df[
    (df["Country"].isin(selected_countries))
    &
    (df["Year"] >= year_range[0])
    &
    (df["Year"] <= year_range[1])
]


if filtered.empty:

    st.warning(
        "No data available for selected filters."
    )

    st.stop()



# Metric selection

if metric == "Total CO2 (Mt)":

    y_col = "CO2_Mt"
    y_label = "CO2 Emissions (Mt)"

else:

    y_col = "CO2_per_capita"
    y_label = "CO2 per Capita (t)"



first_year = filtered["Year"].min()
last_year = filtered["Year"].max()



# ─────────────────────────────────────────────
# Filter summary
# ─────────────────────────────────────────────

st.caption(
    f"""
    **{len(selected_countries)} countries**
    |
    Region: {selected_region}
    |
    {first_year} - {last_year}
    |
    {metric}
    """
)



# ─────────────────────────────────────────────
# KPI calculations
# ─────────────────────────────────────────────

first_data = filtered[
    filtered["Year"] == first_year
]

last_data = filtered[
    filtered["Year"] == last_year
]


total_first = first_data[y_col].sum()

total_last = last_data[y_col].sum()


change = (
    (total_last-total_first)
    /
    total_first
    *
    100
) if total_first else 0



ranked = (
    last_data
    .groupby("Country")[y_col]
    .sum()
    .sort_values(
        ascending=False
    )
)



top_country = ranked.index[0]

top_value = ranked.iloc[0]



c1, c2, c3 = st.columns(3)



c1.metric(
    f"Total {metric} ({last_year})",
    f"{total_last:,.0f}"
)


c2.metric(
    "Change",
    f"{change:+.1f}%"
)


c3.metric(
    f"Highest {metric}",
    top_country,
    help=f"{top_value:,.0f}"
)



st.divider()



# ─────────────────────────────────────────────
# Charts
# ─────────────────────────────────────────────

left, right = st.columns(
    [2,1]
)



# LINE CHART
with left:


    if highlight_top:


        top_country = (
            filtered
            .groupby("Country")[y_col]
            .sum()
            .idxmax()
        )


        fig = go.Figure()


        for country in filtered["Country"].unique():


            temp = filtered[
                filtered["Country"] == country
            ]


            fig.add_trace(
                go.Scatter(

                    x=temp["Date"],

                    y=temp[y_col],

                    mode="lines",

                    name=country,


                    line=dict(

                        color=
                        "#2E75B6"
                        if country == top_country
                        else "#CCCCCC",

                        width=
                        3
                        if country == top_country
                        else 1
                    )
                )
            )


        fig.update_layout(

            title=
            f"<b>{top_country} leads {y_label}</b>",

            plot_bgcolor="white",

            paper_bgcolor="white"
        )


    else:


        fig = px.line(

            filtered.sort_values(
                ["Country","Year"]
            ),

            x="Date",

            y=y_col,

            color="Country",

            title=
            f"<b>{y_label} over time</b>"
        )


        fig.update_layout(

            plot_bgcolor="white",

            paper_bgcolor="white"
        )



    st.plotly_chart(
        fig,
        use_container_width=True
    )




# BAR CHART

with right:


    bar_data = (

        last_data
        .groupby("Country")[y_col]
        .sum()
        .sort_values()
        .tail(15)
        .reset_index()

    )


    fig2 = px.bar(

        bar_data,

        x=y_col,

        y="Country",

        orientation="h",

        title=
        f"<b>Ranking {last_year}</b>"
    )


    fig2.update_layout(

        plot_bgcolor="white",

        paper_bgcolor="white",

        showlegend=False
    )


    st.plotly_chart(

        fig2,

        use_container_width=True

    )