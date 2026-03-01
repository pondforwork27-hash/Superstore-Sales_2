import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

st.set_page_config(
    page_title="Superstore Sales Analytics",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background: linear-gradient(135deg, #0a0f1a 0%, #0f1a2f 100%); }
    .metric-card {
        background: linear-gradient(135deg, #0d1b2a 0%, #1b2a3b 100%);
        border: 1px solid #2d4a6b;
        border-radius: 16px;
        padding: 20px;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 30px rgba(66,153,225,0.2);
        border-color: #4299e1;
    }
    .metric-value { font-size: 2rem; font-weight: 700; color: #fff; line-height: 1.2; }
    .metric-label { font-size: 0.85rem; color: #a0aec0; text-transform: uppercase; letter-spacing: 0.05em; }
    .insight-card {
        background: linear-gradient(135deg, #0d1b2a 0%, #1b2a3b 100%);
        border-left: 4px solid #4299e1;
        border-radius: 12px;
        padding: 18px 22px;
        margin-bottom: 12px;
        color: #f0f0f0;
        transition: all 0.3s ease;
    }
    .insight-card:hover { transform: translateX(4px); box-shadow: 0 8px 20px rgba(0,0,0,0.4); }
    .insight-card.warn  { border-left-color: #ed8936; }
    .insight-card.good  { border-left-color: #48bb78; }
    .insight-card.alert { border-left-color: #e94560; }
    .insight-icon   { font-size: 1.5rem; margin-bottom: 8px; }
    .insight-label  { font-size: 0.75rem; color: #a0aec0; text-transform: uppercase; }
    .insight-value  { font-size: 1.5rem; font-weight: 700; color: #fff; }
    .insight-detail { font-size: 0.85rem; color: #90cdf4; }
    ::-webkit-scrollbar       { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: #0d1b2a; }
    ::-webkit-scrollbar-thumb { background: #2d4a6b; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #4299e1; }
</style>
""", unsafe_allow_html=True)

# ── Plotly dark theme helper ──────────────────────────────────────────────────
# FIX: All charts were missing paper_bgcolor / plot_bgcolor, rendering white backgrounds.
# Centralised here so every chart gets a consistent dark look with one call.
def apply_theme(fig, height=400, geo=False):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e2e8f0",
        title_font_color="#90cdf4",
        legend=dict(bgcolor="rgba(13,27,42,0.8)", bordercolor="#2d4a6b", borderwidth=1),
        xaxis=dict(gridcolor="#1e3a5f", zerolinecolor="#1e3a5f", tickcolor="#4a5568"),
        yaxis=dict(gridcolor="#1e3a5f", zerolinecolor="#1e3a5f", tickcolor="#4a5568"),
    )
    if geo:
        fig.update_layout(geo=dict(
            bgcolor="rgba(0,0,0,0)",
            lakecolor="#0a0f1a",
            landcolor="#0d1b2a",
            subunitcolor="#2d4a6b",
        ))
    return fig


# ── Data Loading ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_data():
    df = pd.read_csv("cleaned_train.csv")

    # Normalise column names (handles casing / whitespace variations)
    canonical = {
        "order date": "Order Date", "ship date": "Ship Date",
        "order id": "Order ID", "customer id": "Customer ID",
        "customer name": "Customer Name", "product name": "Product Name",
        "sub-category": "Sub-Category", "subcategory": "Sub-Category",
        "ship mode": "Ship Mode", "sales": "Sales", "profit": "Profit",
        "discount": "Discount", "quantity": "Quantity",
        "category": "Category", "segment": "Segment",
        "region": "Region", "state": "State", "city": "City",
    }
    remap = {
        c: canonical[c.strip().lower()]
        for c in df.columns
        if c.strip().lower() in canonical and c != canonical[c.strip().lower()]
    }
    if remap:
        df = df.rename(columns=remap)

    df["Order Date"]    = pd.to_datetime(df["Order Date"])
    df["Ship Date"]     = pd.to_datetime(df["Ship Date"])
    df["Year"]          = df["Order Date"].dt.year          # int — needed for date reconstruction
    df["Year_str"]      = df["Year"].astype(str)            # string — discrete Plotly colour scale
    df["Month"]         = df["Order Date"].dt.month
    df["Quarter"]       = df["Order Date"].dt.quarter
    df["DayOfWeek"]     = df["Order Date"].dt.day_name()
    df["Month_Year"]    = df["Order Date"].dt.strftime("%b %Y")
    df["Year_Quarter"]  = df["Order Date"].dt.to_period("Q").astype(str)
    df["Shipping_Days"] = (df["Ship Date"] - df["Order Date"]).dt.days

    us_abbrev = {
        "Alabama": "AL","Alaska": "AK","Arizona": "AZ","Arkansas": "AR","California": "CA",
        "Colorado": "CO","Connecticut": "CT","Delaware": "DE","Florida": "FL","Georgia": "GA",
        "Hawaii": "HI","Idaho": "ID","Illinois": "IL","Indiana": "IN","Iowa": "IA",
        "Kansas": "KS","Kentucky": "KY","Louisiana": "LA","Maine": "ME","Maryland": "MD",
        "Massachusetts": "MA","Michigan": "MI","Minnesota": "MN","Mississippi": "MS","Missouri": "MO",
        "Montana": "MT","Nebraska": "NE","Nevada": "NV","New Hampshire": "NH","New Jersey": "NJ",
        "New Mexico": "NM","New York": "NY","North Carolina": "NC","North Dakota": "ND","Ohio": "OH",
        "Oklahoma": "OK","Oregon": "OR","Pennsylvania": "PA","Rhode Island": "RI","South Carolina": "SC",
        "South Dakota": "SD","Tennessee": "TN","Texas": "TX","Utah": "UT","Vermont": "VT",
        "Virginia": "VA","Washington": "WA","West Virginia": "WV","Wisconsin": "WI","Wyoming": "WY",
    }
    df["State Code"] = df["State"].map(us_abbrev)
    return df


try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# ── Sidebar Filters ───────────────────────────────────────────────────────────
st.sidebar.title("🎯 Dashboard Filters")
st.sidebar.markdown("---")

# FIX: replaced date_input (with its partial-range bugs) with a clean year multiselect.
# Default = all years selected.
all_years     = sorted(df["Year"].unique())
selected_years = st.sidebar.multiselect(
    "📅 Year",
    options=all_years,
    default=all_years,
    placeholder="All years",
)

col1, col2 = st.sidebar.columns(2)
with col1:
    selected_regions  = st.multiselect("🌎 Region",    options=sorted(df["Region"].unique()),    default=[])
    selected_segments = st.multiselect("👥 Segment",   options=sorted(df["Segment"].unique()),   default=[])
with col2:
    selected_categories = st.multiselect("📦 Category",  options=sorted(df["Category"].unique()),  default=[])
    selected_ship_modes = st.multiselect("🚚 Ship Mode", options=sorted(df["Ship Mode"].unique()), default=[])

# FIX: initialise mask as a proper boolean Series aligned to df.index.
# The original `pd.Series([True] * len(df))` had a default 0-based RangeIndex that
# could silently misalign when ANDed with a df-indexed Series after any prior filtering.
mask = pd.Series(True, index=df.index)
if selected_years:      mask &= df["Year"].isin(selected_years)
if selected_regions:    mask &= df["Region"].isin(selected_regions)
if selected_categories: mask &= df["Category"].isin(selected_categories)
if selected_segments:   mask &= df["Segment"].isin(selected_segments)
if selected_ship_modes: mask &= df["Ship Mode"].isin(selected_ship_modes)

filtered_df = df[mask].copy()

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Quick Stats")
st.sidebar.metric("Total Records",    f"{len(filtered_df):,}")
st.sidebar.metric("Total Sales",      f"${filtered_df['Sales'].sum():,.0f}")
st.sidebar.metric("Unique Orders",    f"{filtered_df['Order ID'].nunique():,}")
st.sidebar.metric("Unique Customers", f"{filtered_df['Customer ID'].nunique():,}")

if filtered_df.empty:
    st.warning("⚠️ No data matches the selected filters. Please adjust your filters.")
    st.stop()

# ── Header ────────────────────────────────────────────────────────────────────
year_label = (
    ", ".join(str(y) for y in sorted(selected_years))
    if selected_years and len(selected_years) < len(all_years)
    else "All Years"
)
st.title("🛒 Superstore Sales Analytics Dashboard")
st.markdown(
    f"*Analysing {len(filtered_df):,} transactions · "
    f"{filtered_df['Order Date'].min().strftime('%B %Y')} – "
    f"{filtered_df['Order Date'].max().strftime('%B %Y')} · {year_label}*"
)

# ── KPIs ──────────────────────────────────────────────────────────────────────
total_sales   = filtered_df["Sales"].sum()
total_orders  = filtered_df["Order ID"].nunique()
avg_order_val = total_sales / total_orders if total_orders else 0
total_custs   = filtered_df["Customer ID"].nunique()
avg_shipping  = filtered_df["Shipping_Days"].mean()

# ── KPI metrics that are NOT duplicated in the sidebar Quick Stats ────────────
# Sidebar already shows: Total Records, Total Sales, Unique Orders, Unique Customers
# So we show: Avg Order Value, Avg Shipping, YoY Growth, Repeat Rate, Top Category

# YoY growth (most recent two years in the filtered set)
yoy_growth_val = "N/A"
yoy_growth_sub = "insufficient data"
years_avail = sorted(filtered_df["Year"].unique())
if len(years_avail) >= 2:
    s_curr = filtered_df[filtered_df["Year"] == years_avail[-1]]["Sales"].sum()
    s_prev = filtered_df[filtered_df["Year"] == years_avail[-2]]["Sales"].sum()
    if s_prev > 0:
        pct = (s_curr - s_prev) / s_prev * 100
        yoy_growth_val = f"{'+' if pct >= 0 else ''}{pct:.1f}%"
        yoy_growth_sub = f"{years_avail[-2]} → {years_avail[-1]}"

# Avg orders per customer (more meaningful than repeat rate which is ~98% for this dataset)
avg_orders_per_cust = total_orders / total_custs if total_custs else 0
orders_per_cust_series = filtered_df.groupby("Customer ID")["Order ID"].nunique()
top_10_pct_threshold = orders_per_cust_series.quantile(0.90)
heavy_buyers = (orders_per_cust_series >= top_10_pct_threshold).sum()
orders_sub = f"top 10%: {heavy_buyers:,} customers ≥{int(top_10_pct_threshold)} orders"

# Top category by sales
top_cat     = filtered_df.groupby("Category")["Sales"].sum().idxmax()
top_cat_pct = filtered_df.groupby("Category")["Sales"].sum().max() / total_sales * 100

kpi_data = [
    ("Avg Order Value",    f"${avg_order_val:,.0f}",       "#ed8936", "Per transaction"),
    ("Avg Shipping",       f"{avg_shipping:.1f} days",     "#38b2ac", "Order-to-ship"),
    ("YoY Sales Growth",   yoy_growth_val,                 "#48bb78" if "+" in yoy_growth_val else "#fc8181", yoy_growth_sub),
    ("Avg Orders / Customer", f"{avg_orders_per_cust:.1f}",          "#9f7aea", orders_sub),
    ("Top Category",       top_cat,                        "#4299e1", f"{top_cat_pct:.1f}% of revenue"),
]

cols = st.columns(5)
for col, (label, val, color, sub) in zip(cols, kpi_data):
    with col:
        st.markdown(f"""
        <div style="
            border-top: 3px solid {color};
            border-radius: 4px 4px 12px 12px;
            background: linear-gradient(160deg, #0d1b2a 0%, #111e2e 100%);
            padding: 18px 20px 14px;
        ">
            <div style="font-size:0.68rem;font-weight:700;letter-spacing:0.12em;
                        text-transform:uppercase;color:{color};margin-bottom:10px;">{label}</div>
            <div style="font-size:1.75rem;font-weight:800;color:#f7fafc;
                        line-height:1;font-variant-numeric:tabular-nums;">{val}</div>
            <div style="margin-top:8px;padding-top:8px;border-top:1px solid rgba(255,255,255,0.05);
                        font-size:0.65rem;color:#4a5568;letter-spacing:0.05em;">{sub}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("---")

# ── Sales Overview ────────────────────────────────────────────────────────────
st.header("📈 Sales Overview")
tab1, tab2, tab3 = st.tabs(["📅 Time Series", "🏷️ Category Analysis", "🌍 Geographic"])

with tab1:
    col1, col2 = st.columns(2)

    with col1:
        # FIX: group by Year + Year_str to keep int Year for date reconstruction
        # while using Year_str for colour (int → continuous gradient, str → discrete colours)
        monthly_sales = (
            filtered_df.groupby(["Year", "Year_str", "Month"])["Sales"]
            .sum().reset_index()
        )
        monthly_sales["Date"] = pd.to_datetime(
            monthly_sales[["Year", "Month"]].assign(day=1)
        )
        monthly_sales = monthly_sales.sort_values("Date")

        fig_monthly = px.line(
            monthly_sales, x="Date", y="Sales", color="Year_str",
            title="Monthly Sales — Year-over-Year",
            markers=True,
            color_discrete_sequence=["#4299e1", "#48bb78", "#ed8936", "#9f7aea"],
            labels={"Year_str": "Year"},
        )
        fig_monthly.update_traces(
            line_width=3, marker_size=8,
            hovertemplate="<b>%{x|%B %Y}</b><br>Sales: $%{y:,.0f}<extra></extra>",
        )
        fig_monthly.update_layout(
            xaxis_title="", yaxis_title="Sales ($)", hovermode="x unified",
            xaxis=dict(tickformat="%b %Y", tickangle=-45),
        )
        apply_theme(fig_monthly)
        st.plotly_chart(fig_monthly, use_container_width=True)

    with col2:
        quarterly_sales = (
            filtered_df.groupby(["Year", "Quarter"])["Sales"].sum().reset_index()
        )
        quarterly_sales["Quarter_Label"] = (
            quarterly_sales["Year"].astype(str) + "-Q" + quarterly_sales["Quarter"].astype(str)
        )
        quarterly_sales = quarterly_sales.sort_values(["Year", "Quarter"])

        fig_quarterly = px.bar(
            quarterly_sales, x="Quarter_Label", y="Sales",
            title="Quarterly Sales Performance",
            color="Sales", color_continuous_scale="Blues",
        )
        fig_quarterly.update_traces(
            hovertemplate="<b>%{x}</b><br>Sales: $%{y:,.0f}<extra></extra>"
        )
        fig_quarterly.update_layout(
            xaxis_title="", yaxis_title="Sales ($)",
            coloraxis_showscale=False, xaxis_tickangle=-45,
        )
        apply_theme(fig_quarterly)
        st.plotly_chart(fig_quarterly, use_container_width=True)

with tab2:
    col1, col2, col3 = st.columns(3)

    with col1:
        cat_sales = filtered_df.groupby("Category")["Sales"].sum().reset_index()
        fig_cat = px.pie(
            cat_sales, values="Sales", names="Category", title="Sales by Category",
            color_discrete_sequence=["#1e3a5f", "#2b6cb0", "#4299e1"], hole=0.4,
        )
        fig_cat.update_traces(
            textposition="inside", textinfo="percent+label",
            hovertemplate="<b>%{label}</b><br>Sales: $%{value:,.0f}<br>Share: %{percent}<extra></extra>",
        )
        fig_cat.update_layout(height=350, showlegend=False)
        apply_theme(fig_cat)
        st.plotly_chart(fig_cat, use_container_width=True)

    with col2:
        subcat_sales = (
            filtered_df.groupby("Sub-Category")["Sales"].sum().reset_index().nlargest(10, "Sales")
        )
        fig_subcat = px.bar(
            subcat_sales, x="Sales", y="Sub-Category", orientation="h",
            title="Top 10 Sub-Categories",
            color="Sales", color_continuous_scale="Blues",
        )
        fig_subcat.update_traces(
            hovertemplate="<b>%{y}</b><br>Sales: $%{x:,.0f}<extra></extra>"
        )
        fig_subcat.update_layout(
            yaxis_categoryorder="total ascending", xaxis_title="Sales ($)",
            height=350, coloraxis_showscale=False,
        )
        apply_theme(fig_subcat)
        st.plotly_chart(fig_subcat, use_container_width=True)

    with col3:
        seg_sales = filtered_df.groupby("Segment")["Sales"].sum().reset_index()
        fig_seg = px.bar(
            seg_sales, x="Segment", y="Sales", title="Sales by Customer Segment",
            color="Segment", color_discrete_sequence=["#1e3a5f", "#2b6cb0", "#4299e1"],
        )
        fig_seg.update_traces(
            hovertemplate="<b>%{x}</b><br>Sales: $%{y:,.0f}<extra></extra>"
        )
        fig_seg.update_layout(
            xaxis_title="", yaxis_title="Sales ($)", height=350, showlegend=False,
        )
        apply_theme(fig_seg)
        st.plotly_chart(fig_seg, use_container_width=True)

with tab3:
    col1, col2 = st.columns(2)

    with col1:
        state_sales = (
            filtered_df.groupby(["State", "State Code"])["Sales"].sum().reset_index()
        )
        fig_map = px.choropleth(
            state_sales, locations="State Code", locationmode="USA-states",
            color="Sales", scope="usa", hover_name="State",
            color_continuous_scale=[
                [0, "#0d1b2a"], [0.3, "#1e3a5f"], [0.6, "#2b6cb0"], [1, "#90cdf4"]
            ],
            title="Sales by State",
        )
        # FIX: choropleth uses %{z} for the colour value and %{hovertext} for hover_name.
        # The original used hover_data={'Sales': ':,.2f'} which is a px-only shorthand
        # that doesn't transfer cleanly to update_traces — replaced with explicit hovertemplate.
        fig_map.update_traces(
            hovertemplate="<b>%{hovertext}</b><br>Sales: $%{z:,.0f}<extra></extra>"
        )
        fig_map.update_layout(
            margin={"r": 0, "t": 30, "l": 0, "b": 0},
            coloraxis_colorbar=dict(
                title=dict(text="Sales ($)", font=dict(color="#a0aec0")),
                tickprefix="$",
                tickformat=",.0f",
                bgcolor="rgba(13,27,42,0.8)",
                tickfont=dict(color="#a0aec0"),
            ),
        )
        apply_theme(fig_map, height=400, geo=True)
        st.plotly_chart(fig_map, use_container_width=True)

    with col2:
        top_states = state_sales.nlargest(10, "Sales")
        fig_top_states = px.bar(
            top_states, x="Sales", y="State", orientation="h",
            title="Top 10 States by Sales",
            color="Sales", color_continuous_scale="Blues",
        )
        fig_top_states.update_traces(
            hovertemplate="<b>%{y}</b><br>Sales: $%{x:,.0f}<extra></extra>"
        )
        fig_top_states.update_layout(
            yaxis_categoryorder="total ascending", xaxis_title="Sales ($)",
            coloraxis_showscale=False,
        )
        apply_theme(fig_top_states, height=400)
        st.plotly_chart(fig_top_states, use_container_width=True)

st.markdown("---")

# ── Shipping Analysis ─────────────────────────────────────────────────────────
st.header("🚚 Shipping Performance")
col1, col2, col3 = st.columns(3)

with col1:
    ship_sales = filtered_df.groupby("Ship Mode")["Sales"].sum().reset_index()
    fig_ship = px.pie(
        ship_sales, values="Sales", names="Ship Mode", title="Sales by Shipping Mode",
        color_discrete_sequence=["#1e3a5f", "#2b6cb0", "#4299e1", "#90cdf4"],
    )
    fig_ship.update_traces(
        textposition="inside", textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>Sales: $%{value:,.0f}<br>Share: %{percent}<extra></extra>",
    )
    apply_theme(fig_ship, height=350)
    st.plotly_chart(fig_ship, use_container_width=True)

with col2:
    ship_days = (
        filtered_df.groupby("Ship Mode")["Shipping_Days"]
        .mean().reset_index()
        .sort_values("Shipping_Days", ascending=False)
    )
    fig_ship_days = px.bar(
        ship_days, x="Ship Mode", y="Shipping_Days",
        title="Average Shipping Time by Mode",
        color="Shipping_Days", color_continuous_scale="Blues",
    )
    fig_ship_days.update_traces(
        hovertemplate="<b>%{x}</b><br>Avg Shipping: %{y:.1f} days<extra></extra>"
    )
    fig_ship_days.update_layout(xaxis_title="", yaxis_title="Days", coloraxis_showscale=False)
    apply_theme(fig_ship_days, height=350)
    st.plotly_chart(fig_ship_days, use_container_width=True)

with col3:
    ship_counts = (
        filtered_df.groupby("Ship Mode")["Order ID"].nunique()
        .reset_index().rename(columns={"Order ID": "Order Count"})
        .sort_values("Order Count", ascending=False)
    )
    fig_ship_counts = px.bar(
        ship_counts, x="Ship Mode", y="Order Count",
        title="Orders by Shipping Mode",
        color="Order Count", color_continuous_scale="Blues",
    )
    fig_ship_counts.update_traces(
        hovertemplate="<b>%{x}</b><br>Orders: %{y:,}<extra></extra>"
    )
    fig_ship_counts.update_layout(
        xaxis_title="", yaxis_title="Number of Orders", coloraxis_showscale=False,
    )
    apply_theme(fig_ship_counts, height=350)
    st.plotly_chart(fig_ship_counts, use_container_width=True)

st.markdown("---")

# ── Customer Analysis ─────────────────────────────────────────────────────────
st.header("👥 Customer Insights")
col1, col2 = st.columns(2)

with col1:
    customer_sales = (
        filtered_df.groupby("Customer Name")
        .agg(Total_Sales=("Sales", "sum"), Order_Count=("Order ID", "nunique"))
        .reset_index()
        .nlargest(10, "Total_Sales")
    )
    fig_customers = px.bar(
        customer_sales, x="Total_Sales", y="Customer Name", orientation="h",
        title="Top 10 Customers by Sales",
        color="Total_Sales", color_continuous_scale="Blues",
        custom_data=["Order_Count"],
    )
    fig_customers.update_traces(
        hovertemplate=(
            "<b>%{y}</b><br>Total Sales: $%{x:,.0f}<br>Orders: %{customdata[0]:,}<extra></extra>"
        )
    )
    fig_customers.update_layout(
        yaxis_categoryorder="total ascending", xaxis_title="Sales ($)", coloraxis_showscale=False,
    )
    apply_theme(fig_customers, height=400)
    st.plotly_chart(fig_customers, use_container_width=True)

with col2:
    order_freq = (
        filtered_df.groupby("Customer ID")["Order ID"].nunique()
        .value_counts().sort_index().reset_index()
    )
    order_freq.columns = ["Orders per Customer", "Number of Customers"]
    fig_freq = px.bar(
        order_freq, x="Orders per Customer", y="Number of Customers",
        title="Customer Order Frequency Distribution",
        color="Number of Customers", color_continuous_scale="Blues",
    )
    fig_freq.update_traces(
        hovertemplate="<b>%{x} order(s)</b><br>Customers: %{y:,}<extra></extra>"
    )
    fig_freq.update_layout(
        xaxis_title="Number of Orders", yaxis_title="Number of Customers",
        coloraxis_showscale=False,
    )
    apply_theme(fig_freq, height=400)
    st.plotly_chart(fig_freq, use_container_width=True)

st.markdown("---")

# ── Product Analysis ──────────────────────────────────────────────────────────
st.header("📦 Product Analysis")
col1, col2 = st.columns(2)

with col1:
    subcat_stats = (
        filtered_df.groupby("Sub-Category")
        .agg(Sales=("Sales", "sum"), Orders=("Order ID", "nunique"))
        .reset_index()
    )
    subcat_stats["Avg Order Value"] = subcat_stats["Sales"] / subcat_stats["Orders"]
    subcat_stats = subcat_stats.sort_values("Sales", ascending=False).head(15)

    # FIX: px.scatter size= maps values to pixel area, NOT the original dollar value.
    # Passing Avg Order Value through custom_data ensures the tooltip shows the real amount.
    fig_subcat_perf = px.scatter(
        subcat_stats, x="Orders", y="Sales",
        size="Avg Order Value", color="Sub-Category",
        title="Sub-Category Performance (Top 15)",
        hover_name="Sub-Category",
        custom_data=["Avg Order Value"],
        labels={"Orders": "Number of Orders", "Sales": "Total Sales ($)"},
        size_max=30,
    )
    fig_subcat_perf.update_traces(
        marker=dict(line=dict(width=1, color="white")),
        hovertemplate=(
            "<b>%{hovertext}</b><br>"
            "Sales: $%{y:,.0f}<br>"
            "Orders: %{x:,}<br>"
            "Avg Order: $%{customdata[0]:,.0f}<extra></extra>"
        ),
    )
    fig_subcat_perf.update_layout(
        xaxis_title="Number of Orders", yaxis_title="Total Sales ($)",
        hoverlabel=dict(bgcolor="#0d1b2a", font_size=12, font_color="white"),
    )
    apply_theme(fig_subcat_perf, height=500)
    st.plotly_chart(fig_subcat_perf, use_container_width=True)

    # ── Revenue Intelligence Card ─────────────────────────────────────────────
    top_revenue_sub = subcat_stats.nlargest(1, "Sales").iloc[0]
    top_volume_sub  = subcat_stats.nlargest(1, "Orders").iloc[0]

    rev_name      = str(top_revenue_sub["Sub-Category"])
    vol_name      = str(top_volume_sub["Sub-Category"])
    rev_per_order = float(top_revenue_sub["Avg Order Value"])
    vol_per_order = float(top_volume_sub["Avg Order Value"])
    multiplier    = rev_per_order / vol_per_order if vol_per_order > 0 else 0
    rev_orders    = int(top_revenue_sub["Orders"])
    vol_orders    = int(top_volume_sub["Orders"])

    rev_per_fmt    = f"${rev_per_order:,.0f}"
    vol_per_fmt    = f"${vol_per_order:,.0f}"
    multiplier_fmt = f"{multiplier:.1f}x"
    rev_orders_fmt = f"{rev_orders:,}"
    vol_orders_fmt = f"{vol_orders:,}"
    retention_rev  = f"${rev_per_order * rev_orders * 0.10:,.0f}"

    insight_html = (
        '<div style="margin-top:20px;background:linear-gradient(135deg,#0d1b2a 0%,#111d2e 60%,#0d1b2a 100%);'
        'border:1px solid rgba(159,122,234,0.35);border-radius:18px;overflow:hidden;'
        'box-shadow:0 8px 40px rgba(0,0,0,0.6);position:relative;">'
        '<div style="position:absolute;top:-40px;right:-40px;width:180px;height:180px;'
        'background:radial-gradient(circle,rgba(159,122,234,0.18) 0%,transparent 70%);border-radius:50%;pointer-events:none;"></div>'
        '<div style="position:absolute;bottom:-30px;left:40px;width:120px;height:120px;'
        'background:radial-gradient(circle,rgba(66,153,225,0.12) 0%,transparent 70%);border-radius:50%;pointer-events:none;"></div>'
        '<div style="display:flex;align-items:center;justify-content:space-between;padding:12px 20px;'
        'background:linear-gradient(90deg,rgba(159,122,234,0.12) 0%,transparent 100%);'
        'border-bottom:1px solid rgba(159,122,234,0.2);">'
        '<span style="font-size:0.62rem;font-weight:800;letter-spacing:0.2em;color:#b794f4;text-transform:uppercase;">⚡ Revenue Intelligence</span>'
        '<span style="font-size:0.6rem;font-weight:700;color:#0d1b2a;background:#9f7aea;padding:3px 9px;border-radius:20px;text-transform:uppercase;">Live</span>'
        '</div>'
        '<div style="padding:18px 20px 20px;position:relative;z-index:1;">'
        '<div style="font-size:1.05rem;font-weight:700;color:#f7fafc;line-height:1.35;margin-bottom:4px;">'
        '<span style="color:#b794f4;">' + rev_name + '</span> earns '
        '<span style="display:inline-block;background:rgba(159,122,234,0.15);border:1px solid rgba(159,122,234,0.4);'
        'color:#e9d8fd;font-size:1rem;font-weight:800;padding:1px 8px;border-radius:6px;margin:0 2px;">' + multiplier_fmt + '</span>'
        ' more per order than <span style="color:#90cdf4;">' + vol_name + '</span>'
        '</div>'
        '<div style="font-size:0.75rem;color:#718096;margin-bottom:16px;">Two distinct growth engines — one maximises ticket size, the other repeat frequency.</div>'
        '<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:14px;">'
        '<div style="background:rgba(159,122,234,0.07);border:1px solid rgba(159,122,234,0.22);border-radius:12px;padding:13px 15px;">'
        '<div style="font-size:0.6rem;text-transform:uppercase;letter-spacing:0.14em;color:#b794f4;margin-bottom:5px;font-weight:700;">👑 High-Ticket</div>'
        '<div style="font-size:1.55rem;font-weight:800;color:#fff;">' + rev_per_fmt + '</div>'
        '<div style="font-size:0.68rem;color:#a0aec0;margin-top:3px;">per order · ' + rev_orders_fmt + ' orders</div>'
        '<div style="margin-top:8px;font-size:0.75rem;font-weight:600;color:#e9d8fd;border-top:1px solid rgba(159,122,234,0.15);padding-top:7px;">' + rev_name + '</div>'
        '</div>'
        '<div style="background:rgba(66,153,225,0.07);border:1px solid rgba(66,153,225,0.22);border-radius:12px;padding:13px 15px;">'
        '<div style="font-size:0.6rem;text-transform:uppercase;letter-spacing:0.14em;color:#63b3ed;margin-bottom:5px;font-weight:700;">🔄 High-Volume</div>'
        '<div style="font-size:1.55rem;font-weight:800;color:#fff;">' + vol_per_fmt + '</div>'
        '<div style="font-size:0.68rem;color:#a0aec0;margin-top:3px;">per order · ' + vol_orders_fmt + ' orders</div>'
        '<div style="margin-top:8px;font-size:0.75rem;font-weight:600;color:#bee3f8;border-top:1px solid rgba(66,153,225,0.15);padding-top:7px;">' + vol_name + '</div>'
        '</div>'
        '</div>'
        '<div style="background:rgba(255,255,255,0.025);border-radius:12px;overflow:hidden;">'
        '<div style="padding:9px 14px;border-bottom:1px solid rgba(255,255,255,0.06);display:flex;align-items:center;justify-content:space-between;">'
        '<span style="font-size:0.62rem;font-weight:800;letter-spacing:0.16em;color:#b794f4;text-transform:uppercase;">⚡ The Real Opportunity</span>'
        '<span style="font-size:0.6rem;color:#4a5568;font-style:italic;">Retention, not cross-sell</span>'
        '</div>'
        '<div style="padding:12px 14px;border-bottom:1px solid rgba(255,255,255,0.04);display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;">'
        '<div style="text-align:center;"><div style="font-size:1.1rem;font-weight:800;color:#faf089;">' + rev_per_fmt + '</div>'
        '<div style="font-size:0.62rem;color:#718096;margin-top:2px;">avg order value</div></div>'
        '<div style="text-align:center;border-left:1px solid rgba(255,255,255,0.06);border-right:1px solid rgba(255,255,255,0.06);">'
        '<div style="font-size:1.1rem;font-weight:800;color:#fc8181;">1–2x</div>'
        '<div style="font-size:0.62rem;color:#718096;margin-top:2px;">typical purchase freq.</div></div>'
        '<div style="text-align:center;"><div style="font-size:1.1rem;font-weight:800;color:#68d391;">+10%</div>'
        '<div style="font-size:0.62rem;color:#718096;margin-top:2px;">retention = ' + retention_rev + ' rev</div></div>'
        '</div>'
        '<div style="display:flex;align-items:flex-start;gap:12px;padding:11px 14px;border-bottom:1px solid rgba(255,255,255,0.04);">'
        '<div style="flex-shrink:0;width:22px;height:22px;border-radius:50%;background:rgba(159,122,234,0.2);border:1px solid rgba(159,122,234,0.5);'
        'display:flex;align-items:center;justify-content:center;font-size:0.65rem;font-weight:800;color:#b794f4;">1</div>'
        '<div><div style="font-size:0.75rem;font-weight:700;color:#e2e8f0;margin-bottom:2px;">Flag lapsing high-value customers</div>'
        '<div style="font-size:0.7rem;color:#718096;line-height:1.45;">Identify <strong style="color:#c9b8f5;">' + rev_name + '</strong> '
        "buyers who haven't reordered in 90+ days. Each one lost is " + rev_per_fmt + ' walking out the door.</div></div>'
        '</div>'
        '<div style="display:flex;align-items:flex-start;gap:12px;padding:11px 14px;border-bottom:1px solid rgba(255,255,255,0.04);">'
        '<div style="flex-shrink:0;width:22px;height:22px;border-radius:50%;background:rgba(66,153,225,0.2);border:1px solid rgba(66,153,225,0.5);'
        'display:flex;align-items:center;justify-content:center;font-size:0.65rem;font-weight:800;color:#63b3ed;">2</div>'
        '<div><div style="font-size:0.75rem;font-weight:700;color:#e2e8f0;margin-bottom:2px;">Win them back with an upgrade offer</div>'
        '<div style="font-size:0.7rem;color:#718096;line-height:1.45;">Accessories, extended warranty, or a next-gen model offer. '
        'These buyers already trust the category; the barrier is timing, not intent.</div></div>'
        '</div>'
        '<div style="display:flex;align-items:flex-start;gap:12px;padding:11px 14px;">'
        '<div style="flex-shrink:0;width:22px;height:22px;border-radius:50%;background:rgba(72,187,120,0.2);border:1px solid rgba(72,187,120,0.5);'
        'display:flex;align-items:center;justify-content:center;font-size:0.65rem;font-weight:800;color:#68d391;">3</div>'
        '<div><div style="font-size:0.75rem;font-weight:700;color:#e2e8f0;margin-bottom:2px;">Track repeat rate as a KPI</div>'
        '<div style="font-size:0.7rem;color:#718096;line-height:1.45;">Measure % of ' + rev_name + ' buyers placing a second order within 12 months. '
        'Even lifting that 20% → 30% compounds at ' + rev_per_fmt + ' per order.</div></div>'
        '</div>'
        '</div></div></div>'
    )
    st.markdown(insight_html, unsafe_allow_html=True)

with col2:
    # Segment correlation heatmap
    monthly_segment = (
        filtered_df.groupby(["Year", "Month", "Segment"])["Sales"].sum().reset_index()
    )
    monthly_segment["Date"] = pd.to_datetime(
        monthly_segment[["Year", "Month"]].assign(day=1)
    )
    segment_pivot = (
        monthly_segment.pivot(index="Date", columns="Segment", values="Sales").fillna(0)
    )
    segment_corr = segment_pivot.corr()

    fig_seg_corr = go.Figure(data=go.Heatmap(
        z=segment_corr.values,
        x=segment_corr.columns.tolist(),
        y=segment_corr.index.tolist(),
        colorscale=[
            [0, "#0d1b2a"], [0.25, "#1e3a5f"],
            [0.5, "#2b6cb0"], [0.75, "#4299e1"], [1, "#90cdf4"],
        ],
        # FIX: was zmin=0.5, silently clipping any correlation below 0.5.
        # Set to 0 so the full range is visible.
        zmin=0, zmax=1.0,
        text=[[f"{v:.3f}" for v in row] for row in segment_corr.values],
        texttemplate="%{text}",
        textfont=dict(size=14, color="white"),
        hovertemplate="<b>%{y}</b> vs <b>%{x}</b><br>Correlation: %{z:.3f}<extra></extra>",
    ))
    fig_seg_corr.update_layout(
        title="Segment Sales Correlation<br><sup>How customer segments move together over time</sup>",
        xaxis_title="", yaxis_title="",
    )
    apply_theme(fig_seg_corr, height=500)
    st.plotly_chart(fig_seg_corr, use_container_width=True)

    # Insight cards for strongest / weakest correlation
    segs = segment_corr.columns.tolist()
    corr_pairs = [
        (segs[i], segs[j], segment_corr.iloc[i, j])
        for i in range(len(segs))
        for j in range(i + 1, len(segs))
    ]
    corr_pairs.sort(key=lambda x: x[2], reverse=True)
    strongest = corr_pairs[0]  if corr_pairs else None
    weakest   = corr_pairs[-1] if corr_pairs else None

    ca, cb = st.columns(2)
    with ca:
        if strongest:
            st.markdown(f"""
            <div class="insight-card good" style="margin-top:10px;">
                <div class="insight-icon">📈</div>
                <div class="insight-label">Strongest Correlation</div>
                <div class="insight-value">{strongest[0]} &amp; {strongest[1]}</div>
                <div class="insight-detail">r = <strong>{strongest[2]:.3f}</strong> — These segments move together. Campaigns that boost one will likely lift the other.</div>
            </div>""", unsafe_allow_html=True)
    with cb:
        if weakest:
            st.markdown(f"""
            <div class="insight-card warn" style="margin-top:10px;">
                <div class="insight-icon">📉</div>
                <div class="insight-label">Weakest Correlation</div>
                <div class="insight-value">{weakest[0]} &amp; {weakest[1]}</div>
                <div class="insight-detail">r = <strong>{weakest[2]:.3f}</strong> — These segments behave independently. Tailored strategies recommended.</div>
            </div>""", unsafe_allow_html=True)

    # Segment trend over time
    st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)
    seg_monthly = (
        filtered_df.groupby(["Year", "Month", "Segment"])["Sales"].sum().reset_index()
    )
    seg_monthly["Date"] = pd.to_datetime(seg_monthly[["Year", "Month"]].assign(day=1))
    seg_monthly = seg_monthly.sort_values("Date")

    fig_seg_trend = px.line(
        seg_monthly, x="Date", y="Sales", color="Segment",
        title="Segment Sales Trend Over Time",
        color_discrete_sequence=["#4299e1", "#9f7aea", "#48bb78"],
    )
    fig_seg_trend.update_traces(
        line_width=2.5,
        hovertemplate="<b>%{fullData.name}</b><br>%{x|%b %Y}<br>$%{y:,.0f}<extra></extra>",
    )
    fig_seg_trend.update_layout(
        xaxis_title="", yaxis_title="Sales ($)", legend_title="", hovermode="x unified",
        margin=dict(t=40, b=10, l=0, r=0),
        xaxis=dict(tickformat="%b %Y", tickangle=-30),
    )
    apply_theme(fig_seg_trend, height=240)
    st.plotly_chart(fig_seg_trend, use_container_width=True)

    # Segment share-of-wallet cards
    seg_totals  = filtered_df.groupby("Segment")["Sales"].sum()
    grand_total = seg_totals.sum()
    seg_colors  = {"Consumer": "#4299e1", "Corporate": "#9f7aea", "Home Office": "#48bb78"}
    seg_icons   = {"Consumer": "🛍️",      "Corporate": "🏢",        "Home Office": "🏠"}

    cards_html = '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:4px;">'
    for seg, total in seg_totals.sort_values(ascending=False).items():
        share = total / grand_total * 100
        color = seg_colors.get(seg, "#4299e1")
        icon  = seg_icons.get(seg, "📊")
        cards_html += (
            f'<div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);'
            f'border-top:3px solid {color};border-radius:10px;padding:10px 12px;text-align:center;">'
            f'<div style="font-size:1.1rem;">{icon}</div>'
            f'<div style="font-size:0.62rem;color:#718096;text-transform:uppercase;letter-spacing:0.1em;margin:4px 0 2px;">{seg}</div>'
            f'<div style="font-size:1.1rem;font-weight:800;color:#fff;">{share:.1f}%</div>'
            f'<div style="font-size:0.65rem;color:#4a5568;">of total sales</div>'
            f'<div style="margin-top:6px;height:3px;background:rgba(255,255,255,0.06);border-radius:2px;">'
            f'<div style="height:3px;width:{share:.1f}%;background:{color};border-radius:2px;"></div>'
            f'</div></div>'
        )
    cards_html += "</div>"
    st.markdown(cards_html, unsafe_allow_html=True)

st.markdown("---")

# ── Regional Analysis ─────────────────────────────────────────────────────────
st.header("🌎 Regional Performance")
col1, col2 = st.columns(2)

with col1:
    region_stats = (
        filtered_df.groupby("Region")
        .agg(Sales=("Sales", "sum"), Orders=("Order ID", "nunique"), Customers=("Customer ID", "nunique"))
        .reset_index()
    )
    fig_region = px.bar(
        region_stats, x="Region", y="Sales", title="Sales by Region",
        color="Sales", color_continuous_scale="Blues",
        custom_data=["Orders", "Customers"],
    )
    fig_region.update_traces(
        hovertemplate=(
            "<b>%{x}</b><br>Sales: $%{y:,.0f}<br>"
            "Orders: %{customdata[0]:,}<br>Customers: %{customdata[1]:,}<extra></extra>"
        )
    )
    fig_region.update_layout(xaxis_title="", yaxis_title="Sales ($)", coloraxis_showscale=False)
    apply_theme(fig_region, height=400)
    st.plotly_chart(fig_region, use_container_width=True)

with col2:
    region_cat = filtered_df.groupby(["Region", "Category"])["Sales"].sum().reset_index()
    fig_region_cat = px.bar(
        region_cat, x="Region", y="Sales", color="Category",
        title="Sales by Region and Category", barmode="group",
        color_discrete_sequence=["#1e3a5f", "#2b6cb0", "#4299e1"],
    )
    fig_region_cat.update_traces(
        hovertemplate="<b>%{x}</b> · %{fullData.name}<br>Sales: $%{y:,.0f}<extra></extra>"
    )
    fig_region_cat.update_layout(
        xaxis_title="", yaxis_title="Sales ($)", legend_title="Category",
    )
    apply_theme(fig_region_cat, height=400)
    st.plotly_chart(fig_region_cat, use_container_width=True)

st.markdown("---")

# ── City Performance Table ────────────────────────────────────────────────────
st.header("🏙️ Top Cities by Sales")
city_stats = (
    filtered_df.groupby("City")
    .agg(
        Total_Sales=("Sales", "sum"),
        Orders=("Order ID", "nunique"),
        Customers=("Customer ID", "nunique"),
    )
    .reset_index()
    .nlargest(20, "Total_Sales")
    .rename(columns={"Total_Sales": "Total Sales"})
)
city_stats["Avg Order Value"] = city_stats["Total Sales"] / city_stats["Orders"]
display_df = city_stats.copy()
display_df["Total Sales"]     = display_df["Total Sales"].map("${:,.0f}".format)
display_df["Avg Order Value"] = display_df["Avg Order Value"].map("${:,.0f}".format)

# FIX: was setting .index = range(1, ...) then calling .copy(), making the custom 1-based
# index appear as a column in st.dataframe. Use hide_index=True instead.
st.dataframe(
    display_df,
    use_container_width=True,
    height=400,
    hide_index=True,
    column_config={
        "City":            st.column_config.TextColumn("City"),
        "Total Sales":     st.column_config.TextColumn("Total Sales"),
        "Orders":          st.column_config.NumberColumn("Orders",    format="%d"),
        "Customers":       st.column_config.NumberColumn("Customers", format="%d"),
        "Avg Order Value": st.column_config.TextColumn("Avg Order"),
    },
)

# ── Download ──────────────────────────────────────────────────────────────────
st.markdown("---")
_, col_dl, _ = st.columns([2, 2, 2])
with col_dl:
    st.download_button(
        label="📥 Download Filtered Data (CSV)",
        data=filtered_df.to_csv(index=False),
        file_name=f"superstore_sales_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        use_container_width=True,
    )

st.markdown("---")
st.markdown(
    '<div style="text-align:center;color:#718096;font-size:0.8rem;padding:20px;">'
    "🛒 Superstore Sales Analytics Dashboard · Built with Streamlit</div>",
    unsafe_allow_html=True,
)
