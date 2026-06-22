import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import datetime


st.set_page_config(
    page_title="CO2 Dashboard",
    page_icon="🌱",
    layout="wide"
)


@st.cache_data
def load_data():
    path = Path(__file__).parent.parent / "data" / "co2_emissions.csv"

    df = pd.read_csv(path)

    df["Date"] = pd.to_datetime(
        df["Year"].astype(str) + "-01-01"
    )

    return df


df = load_data()


st.title("🌱 CO2 Emissions Explorer")

st.caption(
    "Source: Our World in Data — ourworldindata.org/co2-emissions"
)


with st.sidebar:

    st.header("Filters")

    regions = ["All"] + sorted(
        df["Region"].dropna().unique()
    )

    selected_region = st.selectbox(
        "Region",
        regions
    )


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


    date_range = st.date_input(
        "Date range",
        value=(
            datetime.date(
                int(df["Year"].min()),1,1
            ),
            datetime.date(
                int(df["Year"].max()),1,1
            )
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


if not selected_countries:
    st.warning("Select at least one country.")
    st.stop()


start = pd.Timestamp(date_range[0])
end = pd.Timestamp(date_range[1])


filtered = df[
    (df["Country"].isin(selected_countries))
    &
    (df["Date"] >= start)
    &
    (df["Date"] <= end)
]


if filtered.empty:
    st.warning("No data available.")
    st.stop()


if metric == "Total CO2 (Mt)":

    y_col = "CO2_Mt"

else:

    y_col = "CO2_per_capita"



last_year = filtered["Year"].max()

first_year = filtered["Year"].min()


last_data = filtered[
    filtered["Year"] == last_year
]


total = last_data[y_col].sum()


top_country = (
    last_data
    .sort_values(y_col, ascending=False)
    .iloc[0]["Country"]
)


c1,c2,c3 = st.columns(3)


c1.metric(
    "Total",
    f"{total:,.0f}"
)


c2.metric(
    "Year",
    last_year
)


c3.metric(
    "Top emitter",
    top_country
)


left,right = st.columns([2,1])


with left:

    fig = px.line(
        filtered.sort_values(
            ["Country","Year"]
        ),
        x="Date",
        y=y_col,
        color="Country"
    )

    fig.update_layout(
        plot_bgcolor="white"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


with right:

    ranking = (
        last_data
        .groupby("Country")[y_col]
        .sum()
        .reset_index()
        .sort_values(
            y_col
        )
    )


    fig2 = px.bar(
        ranking,
        x=y_col,
        y="Country",
        orientation="h"
    )


    st.plotly_chart(
        fig2,
        use_container_width=True
    )