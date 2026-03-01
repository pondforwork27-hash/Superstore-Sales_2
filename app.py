import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import warnings

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Superstore Analytics",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  DESIGN SYSTEM
# ─────────────────────────────────────────────
PALETTE = {
    "bg":        "#080c14",
    "surface":   "#0e1420",
    "surface2":  "#141c2e",
    "border":    "#1e2d45",
    "accent":    "#00c2ff",
    "accent2":   "#ff6b6b",
    "accent3":   "#ffd166",
    "success":   "#06d6a0",
    "muted":     "#4a6080",
    "text":      "#e2eaf4",
    "subtext":   "#7a96b4",
}

CHART_COLORS = ["#00c2ff", "#ff6b6b", "#ffd166", "#06d6a0", "#c77dff", "#ff9f43"]

st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@400;500&family=Inter:wght@300;400;500&display=swap');

  html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}

  .stApp {{
    background: {PALETTE['bg']};
    background-image:
      radial-gradient(ellipse 80% 50% at 20% -10%, rgba(0,194,255,0.07) 0%, transparent 60%),
      radial-gradient(ellipse 60% 40% at 80% 110%, rgba(255,107,107,0.05) 0%, transparent 60%);
  }}

  /* Sidebar */
  [data-testid="stSidebar"] {{
    background: {PALETTE['surface']} !important;
    border-right: 1px solid {PALETTE['border']};
  }}
  [data-testid="stSidebar"] .stRadio label {{ color: {PALETTE['text']}; }}
  [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {{ color: {PALETTE['subtext']}; font-size: 0.82rem; }}
  [data-testid="stSidebarContent"] {{ padding-top: 1.5rem; }}

  /* Headings */
  h1 {{ font-family: 'Syne', sans-serif; font-weight: 800; color: {PALETTE['text']}; letter-spacing: -0.5px; }}
  h2, h3 {{ font-family: 'Syne', sans-serif; font-weight: 600; color: {PALETTE['text']}; }}

  /* Metric cards */
  .kpi-card {{
    background: {PALETTE['surface2']};
    border: 1px solid {PALETTE['border']};
    border-radius: 14px;
    padding: 22px 24px;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
  }}
  .kpi-card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: var(--accent-color, {PALETTE['accent']});
    border-radius: 14px 14px 0 0;
  }}
  .kpi-label {{
    color: {PALETTE['subtext']};
    font-size: 0.72rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    margin-bottom: 8px;
  }}
  .kpi-value {{
    color: {PALETTE['text']};
    font-family: 'Syne', sans-serif;
    font-size: 1.9rem;
    font-weight: 700;
    line-height: 1;
    margin-bottom: 8px;
  }}
  .kpi-delta-pos {{
    color: {PALETTE['success']};
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
  }}
  .kpi-delta-neg {{
    color: {PALETTE['accent2']};
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
  }}
  .kpi-delta-neu {{
    color: {PALETTE['subtext']};
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
  }}

  /* Section headers */
  .section-title {{
    font-family: 'Syne', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    color: {PALETTE['subtext']};
    text-transform: uppercase;
    letter-spacing: 2px;
    margin: 1.5rem 0 1rem;
    display: flex;
    align-items: center;
    gap: 8px;
  }}
  .section-title::after {{
    content: '';
    flex: 1;
    height: 1px;
    background: {PALETTE['border']};
  }}

  /* Tag pills */
  .tag {{
    display: inline-block;
    background: rgba(0,194,255,0.1);
    color: {PALETTE['accent']};
    border: 1px solid rgba(0,194,255,0.2);
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 0.72rem;
    font-family: 'JetBrains Mono', monospace;
  }}

  /* Table */
  .styled-table {{ width: 100%; border-collapse: collapse; }}
  .styled-table th {{
    background: {PALETTE['surface']};
    color: {PALETTE['subtext']};
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    padding: 10px 14px;
    border-bottom: 1px solid {PALETTE['border']};
    text-align: left;
  }}
  .styled-table td {{
    color: {PALETTE['text']};
    font-size: 0.85rem;
    padding: 10px 14px;
    border-bottom: 1px solid rgba(30,45,69,0.5);
  }}
  .styled-table tr:hover td {{ background: {PALETTE['surface']}; }}

  /* Plotly chart container */
  .js-plotly-plot {{ border-radius: 12px; overflow: hidden; }}

  /* Divider */
  hr {{ border-color: {PALETTE['border']}; margin: 1.5rem 0; }}

  /* Streamlit overrides */
  .stSelectbox > div, .stMultiselect > div {{
    background: {PALETTE['surface']} !important;
    border-color: {PALETTE['border']} !important;
    color: {PALETTE['text']} !important;
  }}
  .stTabs [data-baseweb="tab-list"] {{
    background: {PALETTE['surface']} !important;
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
    border: 1px solid {PALETTE['border']};
  }}
  .stTabs [data-baseweb="tab"] {{
    background: transparent !important;
    color: {PALETTE['subtext']} !important;
    border-radius: 8px;
    font-family: 'Syne', sans-serif;
    font-size: 0.85rem;
    font-weight: 600;
  }}
  .stTabs [aria-selected="true"] {{
    background: {PALETTE['surface2']} !important;
    color: {PALETTE['text']} !important;
  }}
  .stCaption {{ color: {PALETTE['muted']} !important; }}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  DATA
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("cleaned_train.csv")
        df["Order Date"] = pd.to_datetime(df["Order Date"])
        df["Ship Date"] = pd.to_datetime(df["Ship Date"])
        df["Year"] = df["Order Date"].dt.year
        df["Quarter"] = df["Order Date"].dt.to_period("Q").astype(str)
        df["Month"] = df["Order Date"].dt.month
        df["Month_Name"] = df["Order Date"].dt.strftime("%b")
        df["DayOfWeek"] = df["Order Date"].dt.day_name()
        df["Shipping_Days"] = (df["Ship Date"] - df["Order Date"]).dt.days

        if "Profit" not in df.columns:
            df["Profit"] = df["Sales"] * 0.25
        if "Discount" not in df.columns:
            df["Discount"] = 0.0

        df["Profit_Margin"] = (df["Profit"] / df["Sales"].replace(0, np.nan)) * 100
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()


# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def fmt_currency(v):
    if abs(v) >= 1e6:
        return f"${v/1e6:.2f}M"
    elif abs(v) >= 1e3:
        return f"${v/1e3:.1f}K"
    return f"${v:,.0f}"


def chart_layout(fig, height=380, margin=None):
    """Apply consistent dark theme to any plotly figure."""
    m = margin or dict(l=20, r=20, t=40, b=20)
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=PALETTE["text"], family="Inter, sans-serif", size=12),
        title_font=dict(family="Syne, sans-serif", size=14, color=PALETTE["subtext"]),
        height=height,
        margin=m,
        legend=dict(
            bgcolor="rgba(14,20,32,0.8)",
            bordercolor=PALETTE["border"],
            borderwidth=1,
        ),
        xaxis=dict(gridcolor=PALETTE["border"], zerolinecolor=PALETTE["border"]),
        yaxis=dict(gridcolor=PALETTE["border"], zerolinecolor=PALETTE["border"]),
        colorway=CHART_COLORS,
    )
    return fig


def kpi_card(label, value, delta=None, accent=None, prefix=""):
    color = accent or PALETTE["accent"]
    delta_html = ""
    if delta is not None:
        sign = "▲" if delta > 0 else "▼"
        cls = "kpi-delta-pos" if delta > 0 else ("kpi-delta-neg" if delta < 0 else "kpi-delta-neu")
        delta_html = f'<div class="{cls}">{sign} {abs(delta):.1f}% vs prior year</div>'
    return f"""
    <div class="kpi-card" style="--accent-color:{color}">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value">{prefix}{value}</div>
      {delta_html}
    </div>"""


def yoy_delta(df, col, agg="sum"):
    years = sorted(df["Year"].unique())
    if len(years) < 2:
        return None
    curr_y, prev_y = years[-1], years[-2]
    curr = df[df["Year"] == curr_y][col].agg(agg)
    prev = df[df["Year"] == prev_y][col].agg(agg)
    if prev == 0:
        return None
    return ((curr - prev) / abs(prev)) * 100


# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
def build_sidebar(df):
    with st.sidebar:
        st.markdown(
            f"""<div style="font-family:'Syne',sans-serif;font-size:1.25rem;
            font-weight:800;color:{PALETTE['text']};letter-spacing:-0.3px;
            margin-bottom:4px;">◈ SUPERSTORE</div>
            <div style="font-size:0.7rem;color:{PALETTE['muted']};
            letter-spacing:2px;text-transform:uppercase;margin-bottom:1.5rem;">Analytics Intelligence</div>""",
            unsafe_allow_html=True,
        )

        page = st.radio(
            "Navigation",
            ["Overview", "Sales Analysis", "Product Insights", "Customer Intelligence", "Geographic"],
            label_visibility="collapsed",
        )

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(
            f'<div style="font-size:0.7rem;color:{PALETTE["subtext"]};'
            f'text-transform:uppercase;letter-spacing:1.5px;margin-bottom:0.8rem;">Filters</div>',
            unsafe_allow_html=True,
        )

        years = sorted(df["Year"].unique())
        selected_years = st.multiselect(
            "Year",
            options=years,
            default=years,
            placeholder="All years",
        )

        regions = sorted(df["Region"].unique()) if "Region" in df.columns else []
        selected_regions = st.multiselect(
            "Region",
            options=regions,
            default=[],
            placeholder="All regions",
        )

        categories = sorted(df["Category"].unique())
        selected_cats = st.multiselect(
            "Category",
            options=categories,
            default=[],
            placeholder="All categories",
        )

        segments = sorted(df["Segment"].unique())
        selected_segs = st.multiselect(
            "Segment",
            options=segments,
            default=[],
            placeholder="All segments",
        )

        st.markdown("<hr>", unsafe_allow_html=True)

    # Apply filters
    fdf = df.copy()
    if selected_years:
        fdf = fdf[fdf["Year"].isin(selected_years)]
    if selected_regions:
        fdf = fdf[fdf["Region"].isin(selected_regions)]
    if selected_cats:
        fdf = fdf[fdf["Category"].isin(selected_cats)]
    if selected_segs:
        fdf = fdf[fdf["Segment"].isin(selected_segs)]

    with st.sidebar:
        st.markdown(
            f'<div style="font-size:0.72rem;color:{PALETTE["muted"]};">'
            f'<span class="tag">{len(fdf):,} records</span></div>',
            unsafe_allow_html=True,
        )

    return page, fdf


# ─────────────────────────────────────────────
#  PAGES
# ─────────────────────────────────────────────
def page_overview(df, raw_df):
    st.markdown("# Executive Overview")

    # KPIs
    total_sales = df["Sales"].sum()
    total_profit = df["Profit"].sum()
    total_orders = df["Order ID"].nunique()
    margin = (total_profit / total_sales * 100) if total_sales else 0
    avg_ship = df["Shipping_Days"].mean()

    d_sales = yoy_delta(df, "Sales")
    d_profit = yoy_delta(df, "Profit")
    d_orders = yoy_delta(raw_df.assign(flag=1).merge(
        df[["Order ID"]].drop_duplicates(), on="Order ID"), "flag", "count") if False else None

    c1, c2, c3, c4, c5 = st.columns(5)
    cards = [
        (c1, "Total Revenue", fmt_currency(total_sales), d_sales, PALETTE["accent"]),
        (c2, "Total Profit", fmt_currency(total_profit), d_profit, PALETTE["success"]),
        (c3, "Profit Margin", f"{margin:.1f}%", None, PALETTE["accent3"]),
        (c4, "Orders", f"{total_orders:,}", None, PALETTE["accent2"]),
        (c5, "Avg Ship Days", f"{avg_ship:.1f}", None, PALETTE["muted"]),
    ]
    for col, label, val, delta, color in cards:
        with col:
            st.markdown(kpi_card(label, val, delta, color), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Row 1: Revenue trend + Category breakdown
    col_l, col_r = st.columns([3, 2])

    with col_l:
        st.markdown('<div class="section-title">Revenue Trend</div>', unsafe_allow_html=True)
        monthly = (
            df.groupby(df["Order Date"].dt.to_period("M").astype(str))
            .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
            .reset_index()
        )
        monthly.columns = ["Period", "Sales", "Profit"]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=monthly["Period"], y=monthly["Sales"],
            name="Revenue", line=dict(color=PALETTE["accent"], width=2),
            fill="tozeroy", fillcolor="rgba(0,194,255,0.07)",
        ))
        fig.add_trace(go.Scatter(
            x=monthly["Period"], y=monthly["Profit"],
            name="Profit", line=dict(color=PALETTE["success"], width=2, dash="dot"),
        ))
        chart_layout(fig, 300)
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-title">By Category</div>', unsafe_allow_html=True)
        cat = df.groupby("Category").agg(
            Sales=("Sales", "sum"), Profit=("Profit", "sum")
        ).reset_index()
        cat["Margin"] = (cat["Profit"] / cat["Sales"] * 100).round(1)

        fig = go.Figure(go.Bar(
            x=cat["Sales"], y=cat["Category"],
            orientation="h",
            marker=dict(
                color=cat["Sales"],
                colorscale=[[0, PALETTE["surface2"]], [1, PALETTE["accent"]]],
                showscale=False,
            ),
            text=cat["Margin"].apply(lambda x: f"{x:.1f}% margin"),
            textposition="inside",
            textfont=dict(color="white", size=11),
        ))
        chart_layout(fig, 300)
        fig.update_layout(xaxis_title="Sales ($)", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    # Row 2: Quarterly performance + Ship mode
    col_l, col_r = st.columns([2, 2])

    with col_l:
        st.markdown('<div class="section-title">Quarterly Performance</div>', unsafe_allow_html=True)
        q = df.groupby(["Year", "Quarter"]).agg(Sales=("Sales", "sum")).reset_index()
        fig = px.bar(
            q, x="Quarter", y="Sales", color="Year",
            color_discrete_sequence=CHART_COLORS,
            barmode="group",
        )
        chart_layout(fig, 300)
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-title">Shipping Mode Split</div>', unsafe_allow_html=True)
        ship = df.groupby("Ship Mode")["Sales"].sum().reset_index()
        fig = px.pie(
            ship, values="Sales", names="Ship Mode",
            hole=0.65,
            color_discrete_sequence=CHART_COLORS,
        )
        fig.update_traces(textposition="outside", textinfo="label+percent")
        chart_layout(fig, 300)
        st.plotly_chart(fig, use_container_width=True)


def page_sales_analysis(df):
    st.markdown("# Sales Analysis")

    tab1, tab2, tab3 = st.tabs(["⏱  Time Patterns", "🏷  Segments", "💸  Discounts"])

    # ── Time Patterns ─────────────────────────────
    with tab1:
        col_l, col_r = st.columns(2)

        with col_l:
            st.markdown('<div class="section-title">Monthly Seasonality</div>', unsafe_allow_html=True)
            month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                           "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            seasonal = df.groupby("Month_Name")["Sales"].sum().reindex(month_order).reset_index()
            seasonal.columns = ["Month", "Sales"]
            fig = go.Figure(go.Bar(
                x=seasonal["Month"], y=seasonal["Sales"],
                marker_color=[
                    PALETTE["accent"] if v == seasonal["Sales"].max()
                    else PALETTE["surface2"] for v in seasonal["Sales"]
                ],
                marker_line_width=0,
            ))
            chart_layout(fig, 340)
            st.plotly_chart(fig, use_container_width=True)

        with col_r:
            st.markdown('<div class="section-title">Day-of-Week Patterns</div>', unsafe_allow_html=True)
            day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            dow = df.groupby("DayOfWeek").agg(
                Sales=("Sales", "mean"), Orders=("Order ID", "nunique")
            ).reindex(day_order).reset_index()
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=dow["DayOfWeek"], y=dow["Sales"],
                name="Avg Sale", marker_color=PALETTE["accent"], opacity=0.85,
            ))
            chart_layout(fig, 340)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown('<div class="section-title">Year-over-Year Comparison</div>', unsafe_allow_html=True)
        yoy = df.groupby(["Year", "Month_Name"])["Sales"].sum().reset_index()
        yoy["Month_Name"] = pd.Categorical(yoy["Month_Name"],
            categories=["Jan","Feb","Mar","Apr","May","Jun",
                        "Jul","Aug","Sep","Oct","Nov","Dec"], ordered=True)
        yoy = yoy.sort_values("Month_Name")
        fig = px.line(
            yoy, x="Month_Name", y="Sales", color="Year",
            color_discrete_sequence=CHART_COLORS, markers=True,
        )
        chart_layout(fig, 320)
        st.plotly_chart(fig, use_container_width=True)

    # ── Segments ──────────────────────────────────
    with tab2:
        col_l, col_r = st.columns(2)

        with col_l:
            st.markdown('<div class="section-title">Segment Revenue & Profit</div>', unsafe_allow_html=True)
            seg = df.groupby("Segment").agg(
                Sales=("Sales", "sum"), Profit=("Profit", "sum")
            ).reset_index()
            fig = go.Figure()
            fig.add_trace(go.Bar(name="Revenue", x=seg["Segment"], y=seg["Sales"],
                                  marker_color=PALETTE["accent"]))
            fig.add_trace(go.Bar(name="Profit", x=seg["Segment"], y=seg["Profit"],
                                  marker_color=PALETTE["success"]))
            fig.update_layout(barmode="group")
            chart_layout(fig, 360)
            st.plotly_chart(fig, use_container_width=True)

        with col_r:
            st.markdown('<div class="section-title">Segment × Category Heatmap</div>', unsafe_allow_html=True)
            heat = df.pivot_table(
                index="Segment", columns="Category", values="Sales", aggfunc="sum"
            ).fillna(0)
            fig = px.imshow(
                heat,
                color_continuous_scale=[[0, PALETTE["bg"]], [0.5, PALETTE["accent"] + "88"], [1, PALETTE["accent"]]],
                text_auto=".2s",
            )
            fig.update_traces(textfont_size=12)
            chart_layout(fig, 360)
            st.plotly_chart(fig, use_container_width=True)

        if "Region" in df.columns:
            st.markdown('<div class="section-title">Region Performance</div>', unsafe_allow_html=True)
            region = df.groupby(["Region", "Segment"])["Sales"].sum().reset_index()
            fig = px.bar(region, x="Region", y="Sales", color="Segment",
                         color_discrete_sequence=CHART_COLORS, barmode="stack")
            chart_layout(fig, 320)
            st.plotly_chart(fig, use_container_width=True)

    # ── Discounts ─────────────────────────────────
    with tab3:
        st.markdown('<div class="section-title">Discount Impact on Profit</div>', unsafe_allow_html=True)
        if df["Discount"].sum() > 0:
            fig = px.scatter(
                df.sample(min(2000, len(df)), random_state=42),
                x="Discount", y="Profit_Margin",
                color="Category", size="Sales",
                color_discrete_sequence=CHART_COLORS,
                opacity=0.65,
                trendline="ols",
                labels={"Discount": "Discount Rate", "Profit_Margin": "Profit Margin (%)"},
            )
            chart_layout(fig, 420)
            st.plotly_chart(fig, use_container_width=True)

            col_l, col_r = st.columns(2)
            with col_l:
                st.markdown('<div class="section-title">Avg Discount by Category</div>', unsafe_allow_html=True)
                disc_cat = df.groupby("Category")["Discount"].mean().reset_index()
                fig = px.bar(disc_cat, x="Category", y="Discount",
                             color="Discount", color_continuous_scale=["#06d6a0", "#ff6b6b"])
                chart_layout(fig, 300)
                st.plotly_chart(fig, use_container_width=True)
            with col_r:
                st.markdown('<div class="section-title">Discount Bucket Analysis</div>', unsafe_allow_html=True)
                df2 = df.copy()
                df2["Disc_Bucket"] = pd.cut(df2["Discount"],
                    bins=[-0.01, 0, 0.1, 0.2, 0.3, 0.5, 1.0],
                    labels=["0%", "1–10%", "11–20%", "21–30%", "31–50%", "50%+"])
                bucket = df2.groupby("Disc_Bucket", observed=True).agg(
                    Profit_Margin=("Profit_Margin", "mean"),
                    Orders=("Order ID", "nunique"),
                ).reset_index()
                fig = px.bar(bucket, x="Disc_Bucket", y="Profit_Margin",
                             color="Profit_Margin",
                             color_continuous_scale=["#ff6b6b", "#ffd166", "#06d6a0"])
                chart_layout(fig, 300)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No discount data available in the dataset.")


def page_product_insights(df):
    st.markdown("# Product Insights")

    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown('<div class="section-title">Sub-Category Sales vs Profit</div>', unsafe_allow_html=True)
        subcat = df.groupby("Sub-Category").agg(
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum"),
            Orders=("Order ID", "nunique"),
        ).reset_index()
        subcat["Margin"] = (subcat["Profit"] / subcat["Sales"] * 100).round(1)
        subcat["Profitable"] = subcat["Profit"] > 0

        fig = px.scatter(
            subcat, x="Sales", y="Profit",
            size="Orders", color="Margin",
            text="Sub-Category",
            color_continuous_scale=["#ff6b6b", "#ffd166", "#06d6a0"],
            labels={"Sales": "Total Sales ($)", "Profit": "Total Profit ($)"},
        )
        fig.update_traces(textposition="top center", textfont_size=10)
        fig.add_hline(y=0, line_dash="dot", line_color=PALETTE["accent2"], opacity=0.5)
        chart_layout(fig, 420)
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-title">Top 10 Sub-Categories by Revenue</div>', unsafe_allow_html=True)
        top10 = subcat.nlargest(10, "Sales")
        fig = go.Figure(go.Bar(
            x=top10["Sales"], y=top10["Sub-Category"],
            orientation="h",
            marker=dict(
                color=top10["Margin"],
                colorscale=["#ff6b6b", "#ffd166", "#06d6a0"],
                showscale=True,
                colorbar=dict(title="Margin %", tickfont=dict(color=PALETTE["subtext"])),
            ),
        ))
        chart_layout(fig, 420)
        fig.update_layout(yaxis=dict(categoryorder="total ascending"))
        st.plotly_chart(fig, use_container_width=True)

    # Loss leaders
    st.markdown('<div class="section-title">Loss Leaders — Sub-Categories with Negative Profit</div>', unsafe_allow_html=True)
    losers = subcat[subcat["Profit"] < 0].sort_values("Profit")
    if len(losers):
        fig = go.Figure(go.Bar(
            x=losers["Sub-Category"], y=losers["Profit"],
            marker_color=PALETTE["accent2"],
        ))
        chart_layout(fig, 260)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.success("No loss-making sub-categories in the current selection.")

    # Top products table
    st.markdown('<div class="section-title">Top 15 Products by Revenue</div>', unsafe_allow_html=True)
    top_prod = (
        df.groupby("Product Name")
        .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"), Orders=("Order ID", "nunique"))
        .reset_index()
        .nlargest(15, "Sales")
    )
    top_prod["Margin"] = (top_prod["Profit"] / top_prod["Sales"] * 100).round(1)
    top_prod["Sales_fmt"] = top_prod["Sales"].apply(fmt_currency)
    top_prod["Profit_fmt"] = top_prod["Profit"].apply(fmt_currency)

    rows = ""
    for _, r in top_prod.iterrows():
        m_color = PALETTE["success"] if r["Margin"] >= 0 else PALETTE["accent2"]
        rows += f"""<tr>
          <td>{r['Product Name'][:55]}{'…' if len(r['Product Name']) > 55 else ''}</td>
          <td style="font-family:'JetBrains Mono',monospace">{r['Sales_fmt']}</td>
          <td style="font-family:'JetBrains Mono',monospace;color:{m_color}">{r['Margin']:.1f}%</td>
          <td style="text-align:center">{r['Orders']}</td>
        </tr>"""

    st.markdown(f"""
    <table class="styled-table">
      <thead><tr>
        <th>Product</th><th>Revenue</th><th>Margin</th><th>Orders</th>
      </tr></thead>
      <tbody>{rows}</tbody>
    </table>""", unsafe_allow_html=True)


def page_customer_intelligence(df):
    st.markdown("# Customer Intelligence")

    # KPIs
    n_cust = df["Customer ID"].nunique()
    avg_ltv = df.groupby("Customer ID")["Sales"].sum().mean()
    avg_orders = df.groupby("Customer ID")["Order ID"].nunique().mean()
    repeat_rate = (df.groupby("Customer ID")["Order ID"].nunique() > 1).mean() * 100

    c1, c2, c3, c4 = st.columns(4)
    for col, label, val, accent in [
        (c1, "Unique Customers", f"{n_cust:,}", PALETTE["accent"]),
        (c2, "Avg Customer LTV", fmt_currency(avg_ltv), PALETTE["success"]),
        (c3, "Avg Orders / Customer", f"{avg_orders:.1f}", PALETTE["accent3"]),
        (c4, "Repeat Purchase Rate", f"{repeat_rate:.1f}%", PALETTE["accent2"]),
    ]:
        with col:
            st.markdown(kpi_card(label, val, accent=accent), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📊  Distribution", "🏆  RFM Segments"])

    with tab1:
        col_l, col_r = st.columns(2)

        with col_l:
            st.markdown('<div class="section-title">LTV Distribution</div>', unsafe_allow_html=True)
            ltv = df.groupby("Customer ID")["Sales"].sum()
            fig = px.histogram(
                ltv, nbins=40,
                color_discrete_sequence=[PALETTE["accent"]],
                labels={"value": "Customer Lifetime Value ($)"},
            )
            fig.update_traces(marker_line_width=0, opacity=0.8)
            chart_layout(fig, 340)
            st.plotly_chart(fig, use_container_width=True)

        with col_r:
            st.markdown('<div class="section-title">Order Frequency</div>', unsafe_allow_html=True)
            freq = df.groupby("Customer ID")["Order ID"].nunique().value_counts().sort_index().reset_index()
            freq.columns = ["Orders", "Customers"]
            fig = go.Figure(go.Bar(
                x=freq["Orders"], y=freq["Customers"],
                marker_color=PALETTE["accent3"], marker_line_width=0,
            ))
            chart_layout(fig, 340)
            fig.update_layout(xaxis_title="Number of Orders", yaxis_title="Customers")
            st.plotly_chart(fig, use_container_width=True)

        if "Segment" in df.columns:
            st.markdown('<div class="section-title">Segment Analysis</div>', unsafe_allow_html=True)
            seg_cust = df.groupby("Segment").agg(
                Revenue=("Sales", "sum"),
                Customers=("Customer ID", "nunique"),
                Margin=("Profit_Margin", "mean"),
            ).reset_index()
            seg_cust["Revenue_per_Customer"] = seg_cust["Revenue"] / seg_cust["Customers"]

            fig = go.Figure()
            fig.add_trace(go.Bar(name="Revenue/Customer", x=seg_cust["Segment"],
                                  y=seg_cust["Revenue_per_Customer"], marker_color=PALETTE["accent"]))
            fig.add_trace(go.Bar(name="Avg Margin %", x=seg_cust["Segment"],
                                  y=seg_cust["Margin"], marker_color=PALETTE["success"],
                                  yaxis="y2"))
            fig.update_layout(
                barmode="group",
                yaxis2=dict(overlaying="y", side="right",
                             gridcolor="transparent",
                             tickfont=dict(color=PALETTE["success"])),
            )
            chart_layout(fig, 320)
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.markdown('<div class="section-title">RFM Segmentation</div>', unsafe_allow_html=True)
        st.caption("Recency · Frequency · Monetary — a classic framework to identify your most valuable customers")

        max_date = df["Order Date"].max()
        rfm = df.groupby("Customer ID").agg(
            Recency=("Order Date", lambda x: (max_date - x.max()).days),
            Frequency=("Order ID", "nunique"),
            Monetary=("Sales", "sum"),
        ).reset_index()

        # Score 1–4
        for col in ["Recency", "Frequency", "Monetary"]:
            reverse = col == "Recency"
            rfm[f"{col}_Score"] = pd.qcut(
                rfm[col], q=4, labels=[4, 3, 2, 1] if reverse else [1, 2, 3, 4], duplicates="drop"
            ).astype(int)

        rfm["RFM_Score"] = rfm["Recency_Score"] + rfm["Frequency_Score"] + rfm["Monetary_Score"]

        def segment(s):
            if s >= 10: return "Champions"
            elif s >= 8: return "Loyal"
            elif s >= 6: return "Potential"
            elif s >= 4: return "At Risk"
            else: return "Lost"

        rfm["Segment"] = rfm["RFM_Score"].apply(segment)
        seg_colors = {
            "Champions": PALETTE["accent"],
            "Loyal": PALETTE["success"],
            "Potential": PALETTE["accent3"],
            "At Risk": "#c77dff",
            "Lost": PALETTE["accent2"],
        }

        col_l, col_r = st.columns([2, 1])

        with col_l:
            fig = px.scatter(
                rfm, x="Recency", y="Monetary",
                size="Frequency", color="Segment",
                color_discrete_map=seg_colors,
                opacity=0.75,
                labels={"Recency": "Days Since Last Order", "Monetary": "Total Spend ($)"},
                hover_data={"Customer ID": True},
            )
            chart_layout(fig, 420)
            st.plotly_chart(fig, use_container_width=True)

        with col_r:
            seg_counts = rfm["Segment"].value_counts().reset_index()
            seg_counts.columns = ["Segment", "Count"]
            fig = px.pie(
                seg_counts, values="Count", names="Segment",
                hole=0.55,
                color="Segment",
                color_discrete_map=seg_colors,
            )
            fig.update_traces(textposition="outside", textinfo="label+percent")
            chart_layout(fig, 420)
            st.plotly_chart(fig, use_container_width=True)

        # Summary table
        summary = rfm.groupby("Segment").agg(
            Customers=("Customer ID", "count"),
            Avg_Spend=("Monetary", "mean"),
            Avg_Frequency=("Frequency", "mean"),
            Avg_Recency=("Recency", "mean"),
        ).reset_index().sort_values("Avg_Spend", ascending=False)

        rows = ""
        for _, r in summary.iterrows():
            dot_color = seg_colors.get(r["Segment"], PALETTE["muted"])
            rows += f"""<tr>
              <td><span style="color:{dot_color}">●</span>  {r['Segment']}</td>
              <td style="font-family:'JetBrains Mono',monospace">{int(r['Customers'])}</td>
              <td style="font-family:'JetBrains Mono',monospace">{fmt_currency(r['Avg_Spend'])}</td>
              <td style="font-family:'JetBrains Mono',monospace">{r['Avg_Frequency']:.1f}</td>
              <td style="font-family:'JetBrains Mono',monospace">{r['Avg_Recency']:.0f}d</td>
            </tr>"""

        st.markdown(f"""
        <table class="styled-table">
          <thead><tr>
            <th>Segment</th><th>Customers</th><th>Avg Spend</th><th>Avg Orders</th><th>Avg Recency</th>
          </tr></thead>
          <tbody>{rows}</tbody>
        </table>""", unsafe_allow_html=True)


def page_geographic(df):
    st.markdown("# Geographic Analysis")

    tab1, tab2 = st.tabs(["🗺  Choropleth Map", "📊  Rankings"])

    with tab1:
        metric = st.selectbox("Metric", ["Sales", "Profit", "Orders"], index=0)

        if metric == "Orders":
            state_data = df.groupby("State")["Order ID"].nunique().reset_index()
            state_data.columns = ["State", "Value"]
            label = "Orders"
        else:
            state_data = df.groupby("State")[metric].sum().reset_index()
            state_data.columns = ["State", "Value"]
            label = f"{metric} ($)"

        fig = px.choropleth(
            state_data,
            locations="State",
            locationmode="USA-states",
            color="Value",
            scope="usa",
            color_continuous_scale=[[0, PALETTE["surface2"]], [0.3, "#1a4a7a"], [1, PALETTE["accent"]]],
            labels={"Value": label},
            hover_data={"Value": ":,.0f"},
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            geo=dict(
                bgcolor="rgba(0,0,0,0)",
                lakecolor=PALETTE["bg"],
                landcolor=PALETTE["surface"],
                subunitcolor=PALETTE["border"],
            ),
            font=dict(color=PALETTE["text"]),
            coloraxis_colorbar=dict(
                bgcolor=PALETTE["surface"],
                tickfont=dict(color=PALETTE["subtext"]),
                title=dict(font=dict(color=PALETTE["subtext"])),
            ),
            height=500,
            margin=dict(l=0, r=0, t=0, b=0),
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        col_l, col_r = st.columns(2)

        with col_l:
            st.markdown('<div class="section-title">Top 15 States by Revenue</div>', unsafe_allow_html=True)
            states = df.groupby("State").agg(
                Sales=("Sales", "sum"), Profit=("Profit", "sum")
            ).nlargest(15, "Sales").reset_index()
            states["Margin"] = (states["Profit"] / states["Sales"] * 100).round(1)
            fig = go.Figure(go.Bar(
                x=states["Sales"], y=states["State"],
                orientation="h",
                marker=dict(color=states["Margin"],
                            colorscale=["#ff6b6b", "#ffd166", "#06d6a0"],
                            showscale=True,
                            colorbar=dict(title="Margin %",
                                          tickfont=dict(color=PALETTE["subtext"]))),
            ))
            chart_layout(fig, 480)
            fig.update_layout(yaxis=dict(categoryorder="total ascending"))
            st.plotly_chart(fig, use_container_width=True)

        with col_r:
            st.markdown('<div class="section-title">Top 15 Cities by Revenue</div>', unsafe_allow_html=True)
            cities = df.groupby(["City", "State"])["Sales"].sum().nlargest(15).reset_index()
            cities["Label"] = cities["City"] + ", " + cities["State"]
            fig = go.Figure(go.Bar(
                x=cities["Sales"], y=cities["Label"],
                orientation="h",
                marker_color=PALETTE["accent3"],
            ))
            chart_layout(fig, 480)
            fig.update_layout(yaxis=dict(categoryorder="total ascending"))
            st.plotly_chart(fig, use_container_width=True)

        if "Region" in df.columns:
            st.markdown('<div class="section-title">Region Profitability</div>', unsafe_allow_html=True)
            region = df.groupby("Region").agg(
                Sales=("Sales", "sum"),
                Profit=("Profit", "sum"),
                Orders=("Order ID", "nunique"),
            ).reset_index()
            region["Margin"] = (region["Profit"] / region["Sales"] * 100).round(2)
            fig = px.bar(
                region, x="Region", y=["Sales", "Profit"],
                color_discrete_sequence=[PALETTE["accent"], PALETTE["success"]],
                barmode="group",
            )
            chart_layout(fig, 320)
            st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────
def main():
    raw_df = load_data()
    if raw_df.empty:
        st.stop()

    page, filtered_df = build_sidebar(raw_df)

    if page == "Overview":
        page_overview(filtered_df, raw_df)
    elif page == "Sales Analysis":
        page_sales_analysis(filtered_df)
    elif page == "Product Insights":
        page_product_insights(filtered_df)
    elif page == "Customer Intelligence":
        page_customer_intelligence(filtered_df)
    elif page == "Geographic":
        page_geographic(filtered_df)


if __name__ == "__main__":
    main()
