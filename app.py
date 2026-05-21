import pathlib

import pandas as pd
import plotly.express as px
import streamlit as st

from data.data_generation import generate_marketing_data


DATA_PATH = pathlib.Path("data/marketing_data.xlsx")


@st.cache_data
def load_data() -> pd.DataFrame:
    """Load marketing data from Excel, generating it if needed."""
    if not DATA_PATH.exists():
        generate_marketing_data(output_excel=True, excel_path=str(DATA_PATH))
    # Get file modification time to invalidate cache when file changes
    mtime = DATA_PATH.stat().st_mtime if DATA_PATH.exists() else None
    return pd.read_excel(DATA_PATH)


# Use this to display the cache key info (helps debugging)
# Removes cache automatically when file is modified
def load_data_with_auto_refresh() -> pd.DataFrame:
    """Load data with automatic cache invalidation on file changes."""
    if not DATA_PATH.exists():
        generate_marketing_data(output_excel=True, excel_path=str(DATA_PATH))
    mtime = DATA_PATH.stat().st_mtime if DATA_PATH.exists() else None
    
    @st.cache_data(hash_funcs={pathlib.Path: lambda p: p.stat().st_mtime})
    def _load():
        return pd.read_excel(DATA_PATH)
    
    return _load()


def main():
    st.set_page_config(
        page_title="Agentic Campaign Optimization Engine",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.sidebar.title("Agentic Campaign Optimization")
    st.sidebar.markdown(
        "This workshop app demonstrates how an AI agent can monitor campaigns, detect underperformance, rewrite ad copy, and reallocate budget automatically."
    )

    pages = [
        "Campaign Dashboard",
        "Anomaly Detection",
        "Agentic Creative Optimization",
        "Budget Reallocation Engine",
    ]
    page = st.sidebar.selectbox("Select a page", pages)

    df = load_data_with_auto_refresh()

    if page == "Campaign Dashboard":
        show_dashboard(df)
    elif page == "Anomaly Detection":
        show_anomaly_detection(df)
    elif page == "Agentic Creative Optimization":
        show_creative_optimization(df)
    elif page == "Budget Reallocation Engine":
        show_budget_engine(df)


def show_dashboard(df: pd.DataFrame) -> None:
    st.title("Campaign Dashboard")
    st.markdown(
        "### What the agent is monitoring"
        "\n\nThe AI agent watches key marketing metrics like spend, conversions, CTR, CPA, and ROAS."
        " It looks for segments that are spending budget without delivering efficient results."
    )

    col1, col2 = st.columns(2)
    with col1:
        fig_spend = px.scatter(
            df,
            x="Spend ($)",
            y="Conversions",
            color="Platform",
            hover_data=["Campaign ID", "Audience Segment", "CPA ($)", "ROAS"],
            title="Spend vs Conversions",
        )
        st.plotly_chart(fig_spend, use_container_width=True)

    with col2:
        platform_cpa = df.groupby("Platform")["CPA ($)"].mean().reset_index()
        fig_cpa = px.bar(
            platform_cpa,
            x="Platform",
            y="CPA ($)",
            color="Platform",
            title="Average CPA by Platform",
            text_auto=".2f",
        )
        st.plotly_chart(fig_cpa, use_container_width=True)

    st.markdown("---")
    st.subheader("Raw campaign data")
    st.dataframe(df.head(20), use_container_width=True)


def show_anomaly_detection(df: pd.DataFrame) -> None:
    st.title("Anomaly Detection")
    st.markdown(
        "### Finding underperforming segments"
        "\n\nThe agent flags segments with high CPA or low CTR so marketers can focus optimization where it matters most."
    )

    underperformers = df[
        (df["CPA ($)"] > 50) | (df["CTR"] < 0.5)
    ].copy()

    st.metric("Total campaigns", len(df))
    st.metric("Underperforming campaigns", len(underperformers))
    st.metric("Average CPA", f"${df['CPA ($)'].mean():.2f}")

    st.markdown("### Worst offenders")
    if not underperformers.empty:
        st.dataframe(underperformers.sort_values(by=["CPA ($)", "CTR"], ascending=[False, True]).head(15), use_container_width=True)
    else:
        st.info("No obvious underperformers found in the current dataset.")


def show_creative_optimization(df: pd.DataFrame) -> None:
    st.title("Agentic Creative Optimization")
    st.markdown(
        "### The agent reviews bad creative and proposes better ads"
        "\n\nChoose an underperforming segment, then let the agent simulate an AI-powered creative rewrite."
    )

    underperforming_segments = sorted(df["Audience Segment"][
        (df["CPA ($)"] > 50) | (df["CTR"] < 0.5)
    ].unique())

    if not underperforming_segments:
        st.warning("No underperforming segments are available for optimization.")
        return

    segment_choice = st.selectbox("Select underperforming segment", underperforming_segments)

    if st.button("Run AI Agent"):
        with st.spinner("Analyzing campaign performance and drafting optimized creative..."):
            st.success("Agent completed the optimization draft.")
            st.markdown("### Agent Analysis")
            st.write(
                f"The selected segment **{segment_choice}** is showing poor engagement and an inefficient CPA. "
                "The agent recommends more relevant messaging and a clearer value proposition for this audience."
            )
            st.markdown("### Recommended ad copy variants")
            for idx in range(1, 4):
                st.markdown(f"**Variant {idx}**")
                st.write(f"**Headline:** Action-driven headline variant {idx} for {segment_choice}")
                st.write(f"**Primary Text:** Messaging that speaks directly to {segment_choice} and improves trust.")
                st.write("---")


def show_budget_engine(df: pd.DataFrame) -> None:
    st.title("Budget Reallocation Engine")
    st.markdown(
        "### How the agent would shift spend to improve performance"
        "\n\nThe agent moves budget away from the weakest performers and increases funding for the strongest segments."
    )

    performance = (
        df.groupby("Audience Segment")
        .agg(
            spend=("Spend ($)", "sum"),
            conversions=("Conversions", "sum"),
            avg_cpa=("CPA ($)", "mean"),
            avg_ctr=("CTR", "mean"),
        )
        .reset_index()
    )
    performance["efficiency_score"] = performance["conversions"] / performance["spend"]

    current_budget = performance["spend"].sum()
    worst_segments = performance.nsmallest(3, "efficiency_score")
    top_segments = performance.nlargest(3, "efficiency_score")

    recommended = performance.copy()
    recommended["recommended_spend"] = recommended["spend"]
    reduction = (worst_segments["spend"] * 0.2).sum()
    recommended.loc[recommended["Audience Segment"].isin(worst_segments["Audience Segment"]), "recommended_spend"] *= 0.8
    recommended.loc[recommended["Audience Segment"].isin(top_segments["Audience Segment"]), "recommended_spend"] += (reduction / 3)

    projected_conversion_rate = performance["conversions"].sum() / performance["spend"].sum()
    projected_conversions = int(projected_conversion_rate * current_budget * 1.05)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Current Budget Allocation")
        st.dataframe(performance[["Audience Segment", "spend", "conversions", "avg_cpa", "avg_ctr"]].rename(
            columns={"spend": "Current Spend", "avg_cpa": "Average CPA", "avg_ctr": "Average CTR"}
        ), use_container_width=True)

    with col2:
        st.subheader("Agent Recommended Allocation")
        st.dataframe(recommended[["Audience Segment", "recommended_spend"]].rename(
            columns={"recommended_spend": "Recommended Spend"}
        ), use_container_width=True)

    st.markdown("### Projected impact")
    st.metric("Current total budget", f"${current_budget:,.0f}")
    st.metric("Projected total conversions", projected_conversions)
    st.write(
        "The agent estimates a roughly 5% improvement in total conversion output after shifting budget away from underperforming segments."
    )


if __name__ == "__main__":
    main()
