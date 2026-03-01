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
    "bg":       "#080c14",
    "surface":  "#0e1420",
    "surface2": "#141c2e",
    "border":   "#1e2d45",
    "accent":   "#00c2ff",
    "accent2":  "#ff6b6b",
    "accent3":  "#ffd166",
    "success":  "#06d6a0",
    "muted":    "#4a6080",
    "text":     "#e2eaf4",
    "subtext":  "#7a96b4",
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

  [data-testid="stSidebar"] {{
    background: {PALETTE['surface']} !important;
    border-right: 1px solid {PALETTE['border']};
  }}
  [data-testid="stSidebar"] .stRadio label {{ color: {PALETTE['text']}; }}
  [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {{ color: {PALETTE['subtext']}; font-size: 0.82rem; }}
  [data-testid="stSidebarContent"] {{ padding-top: 1.5rem; }}

  h1 {{ font-family: 'Syne', sans-serif; font-weight: 800; color: {PALETTE['text']}; letter-spacing: -0.5px; }}
  h2, h3 {{ font-family: 'Syne', sans-serif; font-weight: 600; color: {PALETTE['text']}; }}

  .kpi-card {{
    background: {PALETTE['surface2']};
    border: 1px solid {PALETTE['border']};
    border-radius: 14px;
    padding: 22px 24px;
    position: relative;
    overflow: hidden;
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

  .section-title {{
    font-family: 'Syne', sans-serif;
    font-size: 0.9rem;
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

  .warn-box {{
    background: rgba(255,107,107,0.08);
    border: 1px solid rgba(255,107,107,0.3);
    border-left: 3px solid {PALETTE['accent2']};
    border-radius: 8px;
    padding: 12px 16px;
    color: {PALETTE['accent2']};
    font-size: 0.82rem;
    margin-bottom: 1rem;
  }}

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

  hr {{ border-color: {PALETTE['border']}; margin: 1.5rem 0; }}

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
        df["Ship Date"]  = pd.to_datetime(df["Ship Date"])
        df["Year"]          = df["Order Date"].dt.year
        df["Year_str"]      = df["Year"].astype(str)        # string so Plotly colors years discretely
        df["Quarter"]       = df["Order Date"].dt.to_period("Q").astype(str)
        df["Month"]         = df["Order Date"].dt.month
        df["Month_Name"]    = df["Order Date"].dt.strftime("%b")
        df["DayOfWeek"]     = df["Order Date"].dt.day_name()
        df["Shipping_Days"] = (df["Ship Date"] - df["Order Date"]).dt.days

        # ── FIX: never fabricate Profit as Sales*0.25 — that forces every margin to 25% ──
        # If the column is missing, store real NaN and surface a warning to the user instead.
        has_profit   = "Profit"   in df.columns
        has_discount = "Discount" in df.columns

        if not has_profit:
            df["Profit"] = np.nan
        if not has_discount:
            df["Discount"] = 0.0

        df["Profit_Margin"] = np.where(
            df["Sales"] != 0,
            (df["Profit"] / df["Sales"]) * 100,
            np.nan,
        )

        # Store flags so pages can adapt their layout
        df.attrs["has_profit"]   = has_profit
        df.attrs["has_discount"] = has_discount
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()


# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def fmt_currency(v):
    """Format dollars correctly for negatives: -$1.2M not $-1.2M."""
    if pd.isna(v):
        return "N/A"
    sign = "-" if v < 0 else ""
    a = abs(v)
    if a >= 1e6:
        return f"{sign}${a/1e6:.2f}M"
    if a >= 1e3:
        return f"{sign}${a/1e3:.1f}K"
    return f"{sign}${a:,.0f}"


def fmt_pct(v):
    return "N/A" if pd.isna(v) else f"{v:.1f}%"


def chart_layout(fig, height=380, margin=None, has_axes=True):
    """Unified dark theme. Set has_axes=False for geo/pie/heatmap charts."""
    m = margin or dict(l=20, r=20, t=40, b=20)
    updates = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=PALETTE["text"], family="Inter, sans-serif", size=12),
        title_font=dict(family="Syne, sans-serif", size=14, color=PALETTE["subtext"]),
        height=height,
        margin=m,
        legend=dict(bgcolor="rgba(14,20,32,0.8)", bordercolor=PALETTE["border"], borderwidth=1),
        colorway=CHART_COLORS,
    )
    if has_axes:
        updates["xaxis"] = dict(gridcolor=PALETTE["border"], zerolinecolor=PALETTE["border"])
        updates["yaxis"] = dict(gridcolor=PALETTE["border"], zerolinecolor=PALETTE["border"])
    fig.update_layout(**updates)
    return fig


def kpi_card(label, value, delta=None, accent=None):
    color = accent or PALETTE["accent"]
    delta_html = ""
    if delta is not None and not pd.isna(delta):
        sign = "▲" if delta > 0 else "▼"
        cls  = "kpi-delta-pos" if delta > 0 else ("kpi-delta-neg" if delta < 0 else "kpi-delta-neu")
        delta_html = f'<div class="{cls}">{sign} {abs(delta):.1f}% vs prior year</div>'
    return f"""
    <div class="kpi-card" style="--accent-color:{color}">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value">{value}</div>
      {delta_html}
    </div>"""


def yoy_delta(df, col, agg="sum"):
    """% change between the two most recent years. Returns None when not applicable."""
    years = sorted(df["Year"].dropna().unique())
    if len(years) < 2:
        return None
    curr = df[df["Year"] == years[-1]][col].agg(agg)
    prev = df[df["Year"] == years[-2]][col].agg(agg)
    if pd.isna(prev) or prev == 0:
        return None
    return float(((curr - prev) / abs(prev)) * 100)


def safe_mean(series):
    v = series.mean()
    return None if pd.isna(v) else v


def profit_warning():
    st.markdown(
        '<div class="warn-box">⚠ <strong>Profit column not found</strong> in the dataset — '
        "profit and margin metrics are unavailable.</div>",
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
def build_sidebar(df):
    with st.sidebar:
        st.markdown(
            f"""<div style="font-family:'Syne',sans-serif;font-size:1.25rem;font-weight:800;
            color:{PALETTE['text']};letter-spacing:-0.3px;margin-bottom:4px;">◈ SUPERSTORE</div>
            <div style="font-size:0.7rem;color:{PALETTE['muted']};letter-spacing:2px;
            text-transform:uppercase;margin-bottom:1.5rem;">Analytics Intelligence</div>""",
            unsafe_allow_html=True,
        )

        page = st.radio(
            "Navigation",
            ["Overview", "Sales Analysis", "Product Insights", "Customer Intelligence", "Geographic"],
            label_visibility="collapsed",
        )

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(
            f'<div style="font-size:0.7rem;color:{PALETTE["subtext"]};text-transform:uppercase;'
            f'letter-spacing:1.5px;margin-bottom:0.8rem;">Filters</div>',
            unsafe_allow_html=True,
        )

        years    = sorted(df["Year"].unique())
        sel_years = st.multiselect("Year",     options=years,                           default=years, placeholder="All years")
        regions  = sorted(df["Region"].unique()) if "Region" in df.columns else []
        sel_reg  = st.multiselect("Region",    options=regions,                         default=[],    placeholder="All regions")
        sel_cats = st.multiselect("Category",  options=sorted(df["Category"].unique()), default=[],    placeholder="All categories")
        sel_segs = st.multiselect("Segment",   options=sorted(df["Segment"].unique()),  default=[],    placeholder="All segments")

        st.markdown("<hr>", unsafe_allow_html=True)

    fdf = df.copy()
    if sel_years: fdf = fdf[fdf["Year"].isin(sel_years)]
    if sel_reg:   fdf = fdf[fdf["Region"].isin(sel_reg)]
    if sel_cats:  fdf = fdf[fdf["Category"].isin(sel_cats)]
    if sel_segs:  fdf = fdf[fdf["Segment"].isin(sel_segs)]

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
def page_overview(df):
    st.markdown("# Executive Overview")

    has_profit = df.attrs.get("has_profit", True)
    if not has_profit:
        profit_warning()

    total_sales  = df["Sales"].sum()
    total_profit = df["Profit"].sum()
    total_orders = df["Order ID"].nunique()
    margin       = (total_profit / total_sales * 100) if (total_sales and not pd.isna(total_profit)) else None
    avg_ship     = safe_mean(df["Shipping_Days"])

    d_sales  = yoy_delta(df, "Sales")
    d_profit = yoy_delta(df, "Profit") if has_profit else None

    # FIX: properly compute orders YoY delta (was `if False else None` before)
    years    = sorted(df["Year"].dropna().unique())
    d_orders = None
    if len(years) >= 2:
        curr_ord = df[df["Year"] == years[-1]]["Order ID"].nunique()
        prev_ord = df[df["Year"] == years[-2]]["Order ID"].nunique()
        d_orders = float(((curr_ord - prev_ord) / prev_ord) * 100) if prev_ord else None

    c1, c2, c3, c4, c5 = st.columns(5)
    for col, label, val, delta, accent in [
        (c1, "Total Revenue",  fmt_currency(total_sales),               d_sales,  PALETTE["accent"]),
        (c2, "Total Profit",   fmt_currency(total_profit),              d_profit, PALETTE["success"]),
        (c3, "Profit Margin",  fmt_pct(margin),                         None,     PALETTE["accent3"]),
        (c4, "Orders",         f"{total_orders:,}",                     d_orders, PALETTE["accent2"]),
        (c5, "Avg Ship Days",  f"{avg_ship:.1f}d" if avg_ship else "—", None,     PALETTE["muted"]),
    ]:
        with col:
            st.markdown(kpi_card(label, val, delta, accent), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_l, col_r = st.columns([3, 2])

    with col_l:
        st.markdown('<div class="section-title">Revenue Trend</div>', unsafe_allow_html=True)
        monthly = (
            df.groupby(df["Order Date"].dt.to_period("M").astype(str))
            .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
            .reset_index()
        )
        # rename the index column to "Period" regardless of its auto-name
        monthly.columns = ["Period", "Sales", "Profit"]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=monthly["Period"], y=monthly["Sales"],
            name="Revenue", line=dict(color=PALETTE["accent"], width=2),
            fill="tozeroy", fillcolor="rgba(0,194,255,0.07)",
        ))
        if has_profit:
            fig.add_trace(go.Scatter(
                x=monthly["Period"], y=monthly["Profit"],
                name="Profit", line=dict(color=PALETTE["success"], width=2, dash="dot"),
            ))
        chart_layout(fig, 300)
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-title">By Category</div>', unsafe_allow_html=True)
        cat = df.groupby("Category").agg(Sales=("Sales", "sum"), Profit=("Profit", "sum")).reset_index()
        cat["Margin"] = (cat["Profit"] / cat["Sales"] * 100).round(1)
        fig = go.Figure(go.Bar(
            x=cat["Sales"], y=cat["Category"], orientation="h",
            marker=dict(color=cat["Sales"],
                        colorscale=[[0, PALETTE["surface2"]], [1, PALETTE["accent"]]],
                        showscale=False),
            text=cat["Margin"].apply(lambda x: f"{x:.1f}% margin" if not pd.isna(x) else ""),
            textposition="inside", textfont=dict(color="white", size=11),
        ))
        chart_layout(fig, 300)
        fig.update_layout(xaxis_title="Sales ($)", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown('<div class="section-title">Quarterly Performance</div>', unsafe_allow_html=True)
        # FIX: use Year_str (string) so Plotly assigns discrete colors, not a continuous gradient
        q = df.groupby(["Year_str", "Quarter"]).agg(Sales=("Sales", "sum")).reset_index()
        fig = px.bar(q, x="Quarter", y="Sales", color="Year_str",
                     color_discrete_sequence=CHART_COLORS, barmode="group",
                     labels={"Year_str": "Year"})
        chart_layout(fig, 300)
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-title">Shipping Mode Split</div>', unsafe_allow_html=True)
        ship = df.groupby("Ship Mode")["Sales"].sum().reset_index()
        fig = px.pie(ship, values="Sales", names="Ship Mode",
                     hole=0.65, color_discrete_sequence=CHART_COLORS)
        fig.update_traces(textposition="outside", textinfo="label+percent")
        chart_layout(fig, 300, has_axes=False)  # FIX: no axes on a pie chart
        st.plotly_chart(fig, use_container_width=True)


def page_sales_analysis(df):
    st.markdown("# Sales Analysis")

    has_profit   = df.attrs.get("has_profit", True)
    has_discount = df.attrs.get("has_discount", True)
    month_order  = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

    tab1, tab2, tab3 = st.tabs(["⏱  Time Patterns", "🏷  Segments", "💸  Discounts"])

    with tab1:
        col_l, col_r = st.columns(2)

        with col_l:
            st.markdown('<div class="section-title">Monthly Seasonality</div>', unsafe_allow_html=True)
            seasonal = df.groupby("Month_Name")["Sales"].sum().reindex(month_order).reset_index()
            seasonal.columns = ["Month", "Sales"]
            peak = seasonal["Sales"].max()
            fig = go.Figure(go.Bar(
                x=seasonal["Month"], y=seasonal["Sales"],
                marker_color=[PALETTE["accent"] if v == peak else PALETTE["surface2"]
                              for v in seasonal["Sales"]],
                marker_line_width=0,
            ))
            chart_layout(fig, 340)
            st.plotly_chart(fig, use_container_width=True)

        with col_r:
            st.markdown('<div class="section-title">Day-of-Week Avg Sales</div>', unsafe_allow_html=True)
            day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
            dow = df.groupby("DayOfWeek")["Sales"].mean().reindex(day_order).reset_index()
            dow.columns = ["Day", "Avg Sales"]
            fig = go.Figure(go.Bar(
                x=dow["Day"], y=dow["Avg Sales"],
                marker_color=PALETTE["accent3"], marker_line_width=0,
            ))
            chart_layout(fig, 340)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown('<div class="section-title">Year-over-Year Comparison</div>', unsafe_allow_html=True)
        yoy = df.groupby(["Year_str", "Month_Name"])["Sales"].sum().reset_index()
        yoy["Month_Name"] = pd.Categorical(yoy["Month_Name"], categories=month_order, ordered=True)
        yoy = yoy.sort_values("Month_Name")
        fig = px.line(yoy, x="Month_Name", y="Sales", color="Year_str",
                      color_discrete_sequence=CHART_COLORS, markers=True,
                      labels={"Year_str": "Year", "Month_Name": "Month"})
        chart_layout(fig, 320)
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        col_l, col_r = st.columns(2)

        with col_l:
            st.markdown('<div class="section-title">Segment Revenue & Profit</div>', unsafe_allow_html=True)
            seg = df.groupby("Segment").agg(Sales=("Sales", "sum"), Profit=("Profit", "sum")).reset_index()
            fig = go.Figure()
            fig.add_trace(go.Bar(name="Revenue", x=seg["Segment"], y=seg["Sales"],
                                  marker_color=PALETTE["accent"]))
            if has_profit:
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
                color_continuous_scale=[[0, PALETTE["bg"]], [0.5, PALETTE["accent"]+"88"], [1, PALETTE["accent"]]],
                text_auto=".2s",
            )
            fig.update_traces(textfont_size=12)
            chart_layout(fig, 360, has_axes=False)
            st.plotly_chart(fig, use_container_width=True)

        if "Region" in df.columns:
            st.markdown('<div class="section-title">Region Performance</div>', unsafe_allow_html=True)
            region = df.groupby(["Region", "Segment"])["Sales"].sum().reset_index()
            fig = px.bar(region, x="Region", y="Sales", color="Segment",
                         color_discrete_sequence=CHART_COLORS, barmode="stack")
            chart_layout(fig, 320)
            st.plotly_chart(fig, use_container_width=True)

    with tab3:
        if not has_discount or df["Discount"].sum() == 0:
            st.info("No discount data found in this dataset.")
        else:
            if not has_profit:
                profit_warning()

            st.markdown('<div class="section-title">Discount vs Profit Margin</div>', unsafe_allow_html=True)

            if has_profit:
                sample = df.dropna(subset=["Profit_Margin"]).sample(min(2000, len(df)), random_state=42)
                # FIX: trendline="ols" requires optional dep statsmodels — try it, fall back gracefully
                try:
                    fig = px.scatter(
                        sample, x="Discount", y="Profit_Margin",
                        color="Category", size="Sales",
                        color_discrete_sequence=CHART_COLORS, opacity=0.65,
                        trendline="ols",
                        labels={"Discount": "Discount Rate", "Profit_Margin": "Profit Margin (%)"},
                    )
                except Exception:
                    fig = px.scatter(
                        sample, x="Discount", y="Profit_Margin",
                        color="Category", size="Sales",
                        color_discrete_sequence=CHART_COLORS, opacity=0.65,
                        labels={"Discount": "Discount Rate", "Profit_Margin": "Profit Margin (%)"},
                    )
                chart_layout(fig, 400)
                st.plotly_chart(fig, use_container_width=True)

            col_l, col_r = st.columns(2)
            with col_l:
                st.markdown('<div class="section-title">Avg Discount by Category</div>', unsafe_allow_html=True)
                disc_cat = df.groupby("Category")["Discount"].mean().reset_index()
                fig = px.bar(disc_cat, x="Category", y="Discount",
                             color="Discount",
                             color_continuous_scale=["#06d6a0", "#ffd166", "#ff6b6b"])
                chart_layout(fig, 300)
                st.plotly_chart(fig, use_container_width=True)
            with col_r:
                if has_profit:
                    st.markdown('<div class="section-title">Discount Bucket vs Margin</div>', unsafe_allow_html=True)
                    df2 = df.copy()
                    df2["Disc_Bucket"] = pd.cut(
                        df2["Discount"],
                        bins=[-0.01, 0, 0.1, 0.2, 0.3, 0.5, 1.0],
                        labels=["0%", "1–10%", "11–20%", "21–30%", "31–50%", "50%+"],
                    )
                    bucket = (
                        df2.groupby("Disc_Bucket", observed=True)
                        .agg(Profit_Margin=("Profit_Margin", "mean"), Orders=("Order ID", "nunique"))
                        .reset_index()
                    )
                    fig = px.bar(bucket, x="Disc_Bucket", y="Profit_Margin",
                                 color="Profit_Margin",
                                 color_continuous_scale=["#ff6b6b", "#ffd166", "#06d6a0"],
                                 labels={"Disc_Bucket": "Discount Bracket", "Profit_Margin": "Avg Margin (%)"})
                    chart_layout(fig, 300)
                    st.plotly_chart(fig, use_container_width=True)


def page_product_insights(df):
    st.markdown("# Product Insights")

    has_profit = df.attrs.get("has_profit", True)
    if not has_profit:
        profit_warning()

    subcat = df.groupby("Sub-Category").agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Orders=("Order ID", "nunique"),
    ).reset_index()
    subcat["Margin"] = (subcat["Profit"] / subcat["Sales"] * 100).round(1)

    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown('<div class="section-title">Sub-Category Sales vs Profit</div>', unsafe_allow_html=True)
        fig = px.scatter(
            subcat,
            x="Sales",
            y="Profit" if has_profit else "Sales",
            size="Orders",
            color="Margin" if has_profit else "Sales",
            text="Sub-Category",
            color_continuous_scale=["#ff6b6b", "#ffd166", "#06d6a0"],
            labels={"Sales": "Total Sales ($)", "Profit": "Total Profit ($)"},
        )
        fig.update_traces(textposition="top center", textfont_size=10)
        if has_profit:
            fig.add_hline(y=0, line_dash="dot", line_color=PALETTE["accent2"], opacity=0.5)
        chart_layout(fig, 420)
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-title">Top 10 Sub-Categories by Revenue</div>', unsafe_allow_html=True)
        top10 = subcat.nlargest(10, "Sales")
        if has_profit:
            marker = dict(
                color=top10["Margin"],
                colorscale=["#ff6b6b", "#ffd166", "#06d6a0"],
                showscale=True,
                colorbar=dict(title="Margin %", tickfont=dict(color=PALETTE["subtext"])),
            )
        else:
            marker = dict(color=PALETTE["accent"])
        fig = go.Figure(go.Bar(
            x=top10["Sales"], y=top10["Sub-Category"],
            orientation="h", marker=marker,
        ))
        chart_layout(fig, 420)
        fig.update_layout(yaxis=dict(categoryorder="total ascending"))
        st.plotly_chart(fig, use_container_width=True)

    if has_profit:
        st.markdown(
            '<div class="section-title">Loss Leaders — Sub-Categories with Negative Profit</div>',
            unsafe_allow_html=True,
        )
        losers = subcat[subcat["Profit"] < 0].sort_values("Profit")
        if len(losers):
            fig = go.Figure(go.Bar(
                x=losers["Sub-Category"], y=losers["Profit"],
                marker_color=PALETTE["accent2"],
                text=losers["Profit"].apply(fmt_currency),
                textposition="outside",
            ))
            chart_layout(fig, 260)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.success("No loss-making sub-categories in the current selection.")

    st.markdown('<div class="section-title">Top 15 Products by Revenue</div>', unsafe_allow_html=True)
    top_prod = (
        df.groupby("Product Name")
        .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"), Orders=("Order ID", "nunique"))
        .reset_index()
        .nlargest(15, "Sales")
    )
    top_prod["Margin"] = (top_prod["Profit"] / top_prod["Sales"] * 100).round(1)

    rows = ""
    for _, r in top_prod.iterrows():
        name    = r["Product Name"][:55] + ("…" if len(r["Product Name"]) > 55 else "")
        m_color = PALETTE["success"] if (not pd.isna(r["Margin"]) and r["Margin"] >= 0) else PALETTE["accent2"]
        # FIX: Profit column was computed but never shown in the table previously
        rows += f"""<tr>
          <td>{name}</td>
          <td style="font-family:'JetBrains Mono',monospace">{fmt_currency(r['Sales'])}</td>
          <td style="font-family:'JetBrains Mono',monospace">{fmt_currency(r['Profit'])}</td>
          <td style="font-family:'JetBrains Mono',monospace;color:{m_color}">{fmt_pct(r['Margin'])}</td>
          <td style="text-align:center">{r['Orders']}</td>
        </tr>"""

    st.markdown(f"""
    <table class="styled-table">
      <thead><tr>
        <th>Product</th><th>Revenue</th><th>Profit</th><th>Margin</th><th>Orders</th>
      </tr></thead>
      <tbody>{rows}</tbody>
    </table>""", unsafe_allow_html=True)


def page_customer_intelligence(df):
    st.markdown("# Customer Intelligence")

    n_cust      = df["Customer ID"].nunique()
    avg_ltv     = df.groupby("Customer ID")["Sales"].sum().mean()
    avg_orders  = df.groupby("Customer ID")["Order ID"].nunique().mean()
    repeat_rate = (df.groupby("Customer ID")["Order ID"].nunique() > 1).mean() * 100

    c1, c2, c3, c4 = st.columns(4)
    for col, label, val, accent in [
        (c1, "Unique Customers",      f"{n_cust:,}",           PALETTE["accent"]),
        (c2, "Avg Customer LTV",      fmt_currency(avg_ltv),   PALETTE["success"]),
        (c3, "Avg Orders / Customer", f"{avg_orders:.1f}",     PALETTE["accent3"]),
        (c4, "Repeat Purchase Rate",  f"{repeat_rate:.1f}%",   PALETTE["accent2"]),
    ]:
        with col:
            st.markdown(kpi_card(label, val, accent=accent), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📊  Distribution", "🏆  RFM Segments"])

    with tab1:
        col_l, col_r = st.columns(2)

        with col_l:
            st.markdown('<div class="section-title">LTV Distribution</div>', unsafe_allow_html=True)
            ltv = df.groupby("Customer ID")["Sales"].sum().reset_index()
            ltv.columns = ["Customer ID", "LTV"]
            fig = px.histogram(ltv, x="LTV", nbins=40,
                               color_discrete_sequence=[PALETTE["accent"]],
                               labels={"LTV": "Customer Lifetime Value ($)"})
            fig.update_traces(marker_line_width=0, opacity=0.8)
            chart_layout(fig, 340)
            st.plotly_chart(fig, use_container_width=True)

        with col_r:
            st.markdown('<div class="section-title">Order Frequency</div>', unsafe_allow_html=True)
            freq = (
                df.groupby("Customer ID")["Order ID"].nunique()
                .value_counts().sort_index().reset_index()
            )
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
            fig.add_trace(go.Bar(
                name="Revenue/Customer", x=seg_cust["Segment"],
                y=seg_cust["Revenue_per_Customer"], marker_color=PALETTE["accent"],
            ))
            if df.attrs.get("has_profit", True):
                fig.add_trace(go.Bar(
                    name="Avg Margin %", x=seg_cust["Segment"],
                    y=seg_cust["Margin"].fillna(0), marker_color=PALETTE["success"],
                    yaxis="y2",
                ))
                fig.update_layout(
                    yaxis2=dict(overlaying="y", side="right",
                                gridcolor="transparent",
                                tickfont=dict(color=PALETTE["success"])),
                )
            fig.update_layout(barmode="group")
            chart_layout(fig, 320)
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.markdown('<div class="section-title">RFM Segmentation</div>', unsafe_allow_html=True)
        st.caption("Recency · Frequency · Monetary — identifies your most valuable customers")

        max_date = df["Order Date"].max()
        rfm = df.groupby("Customer ID").agg(
            Recency=("Order Date",  lambda x: (max_date - x.max()).days),
            Frequency=("Order ID", "nunique"),
            Monetary=("Sales",     "sum"),
        ).reset_index()

        # FIX: guard against qcut failing on very small filtered datasets
        if len(rfm) < 8:
            st.warning("Not enough customers in the current selection to compute RFM scores. "
                       "Please broaden your filters.")
        else:
            def safe_qcut(series, q, asc_labels):
                try:
                    return pd.qcut(series, q=q, labels=asc_labels, duplicates="drop").astype(int)
                except ValueError:
                    return pd.Series(2, index=series.index)   # fallback: mid-score

            rfm["R"] = safe_qcut(rfm["Recency"],   4, [4, 3, 2, 1])   # lower recency = better
            rfm["F"] = safe_qcut(rfm["Frequency"], 4, [1, 2, 3, 4])
            rfm["M"] = safe_qcut(rfm["Monetary"],  4, [1, 2, 3, 4])
            rfm["RFM"] = rfm["R"] + rfm["F"] + rfm["M"]

            def label_seg(s):
                if s >= 10: return "Champions"
                if s >= 8:  return "Loyal"
                if s >= 6:  return "Potential"
                if s >= 4:  return "At Risk"
                return "Lost"

            rfm["Segment"] = rfm["RFM"].apply(label_seg)
            seg_colors = {
                "Champions": PALETTE["accent"],
                "Loyal":     PALETTE["success"],
                "Potential": PALETTE["accent3"],
                "At Risk":   "#c77dff",
                "Lost":      PALETTE["accent2"],
            }

            col_l, col_r = st.columns([2, 1])
            with col_l:
                fig = px.scatter(
                    rfm, x="Recency", y="Monetary",
                    size="Frequency", color="Segment",
                    color_discrete_map=seg_colors, opacity=0.75,
                    labels={"Recency": "Days Since Last Order", "Monetary": "Total Spend ($)"},
                    hover_data=["Customer ID"],  # FIX: list syntax, not dict with format string
                )
                chart_layout(fig, 420)
                st.plotly_chart(fig, use_container_width=True)

            with col_r:
                seg_counts = rfm["Segment"].value_counts().reset_index()
                seg_counts.columns = ["Segment", "Count"]
                fig = px.pie(seg_counts, values="Count", names="Segment",
                             hole=0.55, color="Segment", color_discrete_map=seg_colors)
                fig.update_traces(textposition="outside", textinfo="label+percent")
                chart_layout(fig, 420, has_axes=False)
                st.plotly_chart(fig, use_container_width=True)

            summary = (
                rfm.groupby("Segment")
                .agg(Customers=("Customer ID","count"), Avg_Spend=("Monetary","mean"),
                     Avg_Freq=("Frequency","mean"),     Avg_Recency=("Recency","mean"))
                .reset_index()
                .sort_values("Avg_Spend", ascending=False)
            )
            rows = ""
            for _, r in summary.iterrows():
                dot = seg_colors.get(r["Segment"], PALETTE["muted"])
                rows += f"""<tr>
                  <td><span style="color:{dot}">●</span> {r['Segment']}</td>
                  <td style="font-family:'JetBrains Mono',monospace">{int(r['Customers'])}</td>
                  <td style="font-family:'JetBrains Mono',monospace">{fmt_currency(r['Avg_Spend'])}</td>
                  <td style="font-family:'JetBrains Mono',monospace">{r['Avg_Freq']:.1f}</td>
                  <td style="font-family:'JetBrains Mono',monospace">{r['Avg_Recency']:.0f}d</td>
                </tr>"""
            st.markdown(f"""
            <table class="styled-table">
              <thead><tr>
                <th>Segment</th><th>Customers</th><th>Avg Spend</th>
                <th>Avg Orders</th><th>Avg Recency</th>
              </tr></thead>
              <tbody>{rows}</tbody>
            </table>""", unsafe_allow_html=True)


def page_geographic(df):
    st.markdown("# Geographic Analysis")

    has_profit = df.attrs.get("has_profit", True)

    tab1, tab2 = st.tabs(["🗺  Choropleth Map", "📊  Rankings"])

    with tab1:
        options = ["Sales", "Orders"] + (["Profit"] if has_profit else [])
        metric  = st.selectbox("Metric", options, index=0)

        if metric == "Orders":
            state_data = (
                df.groupby("State")["Order ID"].nunique()
                .reset_index().rename(columns={"Order ID": "Value"})
            )
            cb_title  = "Orders"
            hover_fmt = "%{z:,.0f}"
        else:
            state_data = (
                df.groupby("State")[metric].sum()
                .reset_index().rename(columns={metric: "Value"})
            )
            cb_title  = f"{metric} ($)"
            hover_fmt = "$%{z:,.0f}"

        fig = px.choropleth(
            state_data, locations="State", locationmode="USA-states",
            color="Value", scope="usa",
            color_continuous_scale=[[0, PALETTE["surface2"]], [0.3, "#1a4a7a"], [1, PALETTE["accent"]]],
            labels={"Value": cb_title},
        )
        # FIX: use hovertemplate — hover_data format string dict syntax is not valid Plotly
        fig.update_traces(
            hovertemplate="<b>%{location}</b><br>" + cb_title + ": " + hover_fmt + "<extra></extra>"
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            geo=dict(bgcolor="rgba(0,0,0,0)", lakecolor=PALETTE["bg"],
                     landcolor=PALETTE["surface"], subunitcolor=PALETTE["border"]),
            font=dict(color=PALETTE["text"]),
            coloraxis_colorbar=dict(
                bgcolor=PALETTE["surface"],
                tickfont=dict(color=PALETTE["subtext"]),
                title=dict(font=dict(color=PALETTE["subtext"])),
            ),
            height=500, margin=dict(l=0, r=0, t=10, b=0),
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        col_l, col_r = st.columns(2)

        with col_l:
            st.markdown('<div class="section-title">Top 15 States by Revenue</div>', unsafe_allow_html=True)
            states = (
                df.groupby("State")
                .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
                .nlargest(15, "Sales").reset_index()
            )
            states["Margin"] = (states["Profit"] / states["Sales"] * 100).round(1)
            if has_profit:
                marker = dict(color=states["Margin"],
                              colorscale=["#ff6b6b", "#ffd166", "#06d6a0"], showscale=True,
                              colorbar=dict(title="Margin %", tickfont=dict(color=PALETTE["subtext"])))
            else:
                marker = dict(color=PALETTE["accent"])
            fig = go.Figure(go.Bar(
                x=states["Sales"], y=states["State"], orientation="h", marker=marker,
            ))
            chart_layout(fig, 480)
            fig.update_layout(yaxis=dict(categoryorder="total ascending"))
            st.plotly_chart(fig, use_container_width=True)

        with col_r:
            st.markdown('<div class="section-title">Top 15 Cities by Revenue</div>', unsafe_allow_html=True)
            cities = (
                df.groupby(["City", "State"])["Sales"].sum()
                .nlargest(15).reset_index()
            )
            cities["Label"] = cities["City"] + ", " + cities["State"]
            fig = go.Figure(go.Bar(
                x=cities["Sales"], y=cities["Label"],
                orientation="h", marker_color=PALETTE["accent3"],
            ))
            chart_layout(fig, 480)
            fig.update_layout(yaxis=dict(categoryorder="total ascending"))
            st.plotly_chart(fig, use_container_width=True)

        if "Region" in df.columns:
            st.markdown('<div class="section-title">Region Profitability</div>', unsafe_allow_html=True)
            region = df.groupby("Region").agg(
                Sales=("Sales", "sum"), Profit=("Profit", "sum"), Orders=("Order ID", "nunique")
            ).reset_index()
            y_cols = ["Sales"] + (["Profit"] if has_profit else [])
            fig = px.bar(region, x="Region", y=y_cols,
                         color_discrete_sequence=[PALETTE["accent"], PALETTE["success"]],
                         barmode="group")
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

    # Propagate data-quality flags through the filter copy
    filtered_df.attrs["has_profit"]   = raw_df.attrs.get("has_profit",   True)
    filtered_df.attrs["has_discount"] = raw_df.attrs.get("has_discount", True)

    if page == "Overview":
        page_overview(filtered_df)
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
