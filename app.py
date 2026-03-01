import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
import warnings

warnings.filterwarnings("ignore")

# ── Page Configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Superstore Analytics Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS & Theme ────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #f8fafc;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .metric-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(148, 163, 184, 0.1);
        border-radius: 12px;
        padding: 20px;
        transition: transform 0.2s;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        height: 100%;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: #38bdf8;
        box-shadow: 0 10px 15px -3px rgba(56, 189, 248, 0.1);
    }
    .metric-label { font-size: 0.85rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600; }
    .metric-value { font-size: 1.8rem; font-weight: 700; color: #f1f5f9; margin-top: 5px; }
    .metric-delta { font-size: 0.8rem; color: #4ade80; margin-top: 5px; font-weight: 600; }
    .metric-delta.neg { color: #f87171; }
    .insight-box {
        background: rgba(15, 23, 42, 0.6);
        border-left: 4px solid #38bdf8;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 15px;
    }
    .insight-box.warn { border-left-color: #fbbf24; }
    .insight-box.danger { border-left-color: #f87171; }
    .insight-box.good { border-left-color: #4ade80; }
    .revenue-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid rgba(159, 122, 234, 0.3);
        border-radius: 16px;
        padding: 20px;
        margin-top: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    .revenue-header {
        color: #c4b5fd;
        font-size: 0.9rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 15px;
        border-bottom: 1px solid rgba(159, 122, 234, 0.2);
        padding-bottom: 10px;
    }
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #0f172a; }
    ::-webkit-scrollbar-thumb { background: #334155; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #475569; }
    .js-plotly-plot .plotly .modebar { background: rgba(30, 41, 59, 0.5) !important; }
</style>
""", unsafe_allow_html=True)

# ── Helper Functions ──────────────────────────────────────────────────────────

@st.cache_data(ttl=3600)
def load_data():
    try:
        df = pd.read_csv('cleaned_train.csv')
        df['Order Date'] = pd.to_datetime(df['Order Date'])
        df['Ship Date'] = pd.to_datetime(df['Ship Date'])
        df['Year'] = df['Order Date'].dt.year
        df['Month'] = df['Order Date'].dt.month
        df['Month_Name'] = df['Order Date'].dt.month_name()
        df['DayOfWeek'] = df['Order Date'].dt.day_name()
        df['Shipping_Days'] = (df['Ship Date'] - df['Order Date']).dt.days
        
        if 'Profit' not in df.columns:
            df['Profit'] = df['Sales'] * 0.25
            df['Profit Margin'] = 25.0
        else:
            df['Profit Margin'] = (df['Profit'] / df['Sales']) * 100
        
        us_state_to_abbrev = {
            "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
            "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "Florida": "FL", "Georgia": "GA",
            "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA",
            "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
            "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO",
            "Montana": "MT", "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ",
            "New Mexico": "NM", "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH",
            "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
            "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT",
            "Virginia": "VA", "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY"
        }
        df['State Code'] = df['State'].map(us_state_to_abbrev)
        return df
    except Exception as e:
        st.error(f"Critical Error Loading Data: {e}")
        return pd.DataFrame()

# ✅ FIXED: Return layout properties directly (not nested under 'layout' key)
def get_plotly_theme():
    return {
        'font': {'color': '#94a3b8', 'family': 'Inter, sans-serif'},
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'xaxis': {'gridcolor': '#1e293b', 'linecolor': '#1e293b'},
        'yaxis': {'gridcolor': '#1e293b', 'linecolor': '#1e293b'},
        'hovermode': 'x unified',
        'hoverlabel': {'bgcolor': '#0f172a', 'font_color': '#f8fafc', 'bordercolor': '#334155'}
    }

# ── Render Functions ──────────────────────────────────────────────────────────

def render_sidebar(df):
    with st.sidebar:
        st.title("🎛️ Control Center")
        st.markdown("---")
        st.markdown("### 🧭 Navigation")
        nav_selection = st.radio(
            "Go to",
            ["Overview", "Sales Analysis", "Product Insights", "Customer Intelligence", "Geographic Map"],
            label_visibility="collapsed"
        )
        st.markdown("---")
        st.markdown("### 🔍 Filters")
        
        min_date = df['Order Date'].min()
        max_date = df['Order Date'].max()
        
        date_range = st.date_input(
            "📅 Date Range",
            value=[min_date, max_date],
            min_value=min_date,
            max_value=max_date
        )
        
        regions = st.multiselect("Region", options=sorted(df['Region'].unique()), default=[])
        categories = st.multiselect("Category", options=sorted(df['Category'].unique()), default=[])
        segments = st.multiselect("Segment", options=sorted(df['Segment'].unique()), default=[])
        
        st.markdown("---")
        st.caption(f"Data Source: cleaned_train.csv")
        st.caption(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
    return nav_selection, date_range, regions, categories, segments

def apply_filters(df, date_range, regions, categories, segments):
    mask = pd.Series([True] * len(df))
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        mask &= (df['Order Date'] >= pd.Timestamp(start_date)) & (df['Order Date'] <= pd.Timestamp(end_date))
    
    if regions: mask &= df['Region'].isin(regions)
    if categories: mask &= df['Category'].isin(categories)
    if segments: mask &= df['Segment'].isin(segments)
    
    return df[mask].copy()

def render_revenue_intelligence(df):
    subcat_stats = df.groupby('Sub-Category').agg({'Sales': 'sum', 'Order ID': 'nunique'}).reset_index()
    if subcat_stats.empty:
        return

    subcat_stats['Avg Order Value'] = subcat_stats['Sales'] / subcat_stats['Order ID']
    top_revenue_sub = subcat_stats.nlargest(1, 'Sales').iloc[0]
    top_volume_sub  = subcat_stats.nlargest(1, 'Order ID').iloc[0]

    rev_name = str(top_revenue_sub['Sub-Category'])
    vol_name = str(top_volume_sub['Sub-Category'])
    rev_per_order = float(top_revenue_sub['Sales']) / float(top_revenue_sub['Order ID'])
    vol_per_order = float(top_volume_sub['Sales'])  / float(top_volume_sub['Order ID'])
    multiplier = rev_per_order / vol_per_order if vol_per_order > 0 else 0
    
    if rev_name == vol_name:
        insight_text = f"**{rev_name}** dominates both revenue and volume."
    else:
        insight_text = f"**{rev_name}** earns **{multiplier:.1f}x** more per order than **{vol_name}**."

    st.markdown(f"""
    <div class="revenue-card">
        <div class="revenue-header">⚡ Revenue Intelligence</div>
        <div style="color: #f1f5f9; font-size: 1.1rem; margin-bottom: 15px;">
            {insight_text}
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
            <div style="background: rgba(159, 122, 234, 0.1); padding: 10px; border-radius: 8px; border: 1px solid rgba(159, 122, 234, 0.2);">
                <div style="color: #c4b5fd; font-size: 0.7rem; text-transform: uppercase;">High Ticket</div>
                <div style="color: #fff; font-size: 1.4rem; font-weight: bold;">${rev_per_order:,.0f}</div>
                <div style="color: #94a3b8; font-size: 0.8rem;">{rev_name}</div>
            </div>
            <div style="background: rgba(56, 189, 248, 0.1); padding: 10px; border-radius: 8px; border: 1px solid rgba(56, 189, 248, 0.2);">
                <div style="color: #7dd3fc; font-size: 0.7rem; text-transform: uppercase;">High Volume</div>
                <div style="color: #fff; font-size: 1.4rem; font-weight: bold;">${vol_per_order:,.0f}</div>
                <div style="color: #94a3b8; font-size: 0.8rem;">{vol_name}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_overview(df):
    st.title("📊 Executive Overview")
    st.markdown(f"*Real-time analysis of **{len(df):,}** transactions.*")
    
    total_sales = df['Sales'].sum()
    total_profit = df['Profit'].sum()
    total_orders = df['Order ID'].nunique()
    avg_shipping = df['Shipping_Days'].mean()
    profit_margin = (total_profit / total_sales) * 100 if total_sales > 0 else 0
    
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    with kpi1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Revenue</div>
            <div class="metric-value">${total_sales:,.0f}</div>
            <div class="metric-delta">↗ vs Previous Period</div>
        </div>
        """, unsafe_allow_html=True)
        
    with kpi2:
        delta_class = "neg" if profit_margin < 15 else ""
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Net Profit</div>
            <div class="metric-value">${total_profit:,.0f}</div>
            <div class="metric-delta {delta_class}">{profit_margin:.1f}% Margin</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Orders</div>
            <div class="metric-value">{total_orders:,}</div>
            <div class="metric-delta">Active Transactions</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Avg Shipping</div>
            <div class="metric-value">{avg_shipping:.1f} Days</div>
            <div class="metric-delta">Logistics Efficiency</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📈 Revenue Trend")
        monthly_sales = df.groupby(df['Order Date'].dt.to_period('M'))['Sales'].sum().reset_index()
        monthly_sales['Order Date'] = monthly_sales['Order Date'].dt.to_timestamp()
        
        fig_trend = px.line(monthly_sales, x='Order Date', y='Sales', markers=True)
        fig_trend.update_layout(**get_plotly_theme(), height=400, margin=dict(l=0,r=0,t=0,b=0))
        fig_trend.update_traces(line_color='#38bdf8', line_width=3)
        st.plotly_chart(fig_trend, use_container_width=True)
        
    with col2:
        st.subheader("🏷️ Category Mix")
        cat_sales = df.groupby('Category')['Sales'].sum().reset_index()
        fig_pie = px.pie(cat_sales, values='Sales', names='Category', hole=0.6)
        fig_pie.update_layout(**get_plotly_theme(), height=400, margin=dict(l=0,r=0,t=0,b=0))
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("### 💡 Strategic Insights")
    render_revenue_intelligence(df)

def render_sales_analysis(df):
    st.title("💰 Sales Deep Dive")
    
    tab1, tab2 = st.tabs(["Time Series", "Segment Performance"])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            pivot_df = df.pivot_table(values='Sales', index='Month_Name', columns='DayOfWeek', aggfunc='sum')
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            pivot_df = pivot_df.reindex(columns=[d for d in day_order if d in pivot_df.columns])
            
            fig_heat = px.imshow(pivot_df, aspect="auto", color_continuous_scale='Blues')
            fig_heat.update_layout(**get_plotly_theme(), height=400, title="Sales Heatmap (Day vs Month)")
            st.plotly_chart(fig_heat, use_container_width=True)
            
        with col2:
            st.subheader("🚚 Shipping Mode Efficiency")
            ship_df = df.groupby('Ship Mode').agg({'Sales': 'sum', 'Shipping_Days': 'mean'}).reset_index()
            fig_ship = px.bar(ship_df, x='Ship Mode', y='Sales', color='Shipping_Days', 
                              title="Sales vs Avg Shipping Days", color_continuous_scale='Reds')
            fig_ship.update_layout(**get_plotly_theme(), height=400)
            st.plotly_chart(fig_ship, use_container_width=True)

    with tab2:
        st.subheader("👥 Segment Correlation")
        seg_pivot = df.pivot_table(values='Sales', index=df['Order Date'].dt.to_period('M'), columns='Segment', aggfunc='sum')
        corr = seg_pivot.corr()
        
        fig_corr = px.imshow(corr, text_auto='.2f', aspect="auto", color_continuous_scale='RdBu_r')
        fig_corr.update_layout(**get_plotly_theme(), height=500, title="Segment Sales Correlation Matrix")
        st.plotly_chart(fig_corr, use_container_width=True)

def render_product_insights(df):
    st.title("📦 Product Intelligence")
    
    subcat_df = df.groupby('Sub-Category').agg({'Sales': 'sum', 'Profit': 'sum', 'Order ID': 'nunique'}).reset_index()
    subcat_df['Profit Margin'] = (subcat_df['Profit'] / subcat_df['Sales']) * 100
    subcat_df = subcat_df.sort_values('Sales', ascending=False).head(15)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🏆 Top Sub-Categories (Sales vs Margin)")
        fig_scatter = px.scatter(subcat_df, x='Sales', y='Profit Margin', size='Order ID', 
                                 color='Sub-Category', hover_name='Sub-Category',
                                 title="Performance Matrix: High Sales & High Margin are the Goal",
                                 color_continuous_scale='Viridis')
        fig_scatter.update_layout(**get_plotly_theme(), height=500)
        fig_scatter.add_hline(y=0, line_dash="dash", line_color="red", annotation_text="Break-even")
        st.plotly_chart(fig_scatter, use_container_width=True)
        
    with col2:
        st.subheader("⚠️ Profitability Alerts")
        loss_subs = subcat_df[subcat_df['Profit'] < 0]
        
        if not loss_subs.empty:
            for _, row in loss_subs.head(5).iterrows():
                st.markdown(f"""
                <div class="insight-box danger">
                    <strong>{row['Sub-Category']}</strong><br>
                    Loss: ${abs(row['Profit']):,.0f}<br>
                    <small>Margin: {row['Profit Margin']:.1f}%</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("All sub-categories are currently profitable!")

def render_customer_intelligence(df):
    st.title("👥 Customer 360")
    
    rfm = df.groupby('Customer ID').agg({
        'Order Date': 'max',
        'Order ID': 'count',
        'Sales': 'sum'
    }).reset_index()
    
    rfm.columns = ['Customer ID', 'LastPurchase', 'Frequency', 'Monetary']
    rfm['Recency'] = (datetime.now() - rfm['LastPurchase']).dt.days
    
    try:
        rfm['R_Score'] = pd.qcut(rfm['Recency'], 4, labels=[4, 3, 2, 1], duplicates='drop')
        rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 4, labels=[1, 2, 3, 4], duplicates='drop')
        rfm['M_Score'] = pd.qcut(rfm['Monetary'], 4, labels=[1, 2, 3, 4], duplicates='drop')
        
        rfm['Segment'] = rfm['R_Score'].astype(int) + rfm['F_Score'].astype(int) + rfm['M_Score'].astype(int)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎯 Customer Segments")
            seg_counts = rfm['Segment'].value_counts().reset_index()
            seg_counts.columns = ['Score', 'Count']
            seg_counts['Label'] = seg_counts['Score'].apply(lambda x: "Champions" if x >= 10 else "At Risk" if x <= 5 else "Loyal")
            
            fig_seg = px.bar(seg_counts, x='Label', y='Count', color='Count', title="Customer Value Distribution")
            fig_seg.update_layout(**get_plotly_theme(), height=400)
            st.plotly_chart(fig_seg, use_container_width=True)
            
        with col2:
            st.subheader("💎 Top 10 VIP Customers")
            top_cust = rfm.sort_values('Monetary', ascending=False).head(10)
            st.dataframe(top_cust[['Customer ID', 'Monetary', 'Frequency']].style.format({'Monetary': '${:,.0f}'}), height=400)
    except Exception as e:
        st.warning(f"RFM Analysis skipped due to data sparsity: {e}")

def render_geographic_map(df):
    st.title("🌍 Geographic Performance")
    
    state_data = df.groupby(['State', 'State Code']).agg({'Sales': 'sum', 'Profit': 'sum'}).reset_index()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig_map = px.choropleth(state_data, locations='State Code', locationmode="USA-states",
                                color='Sales', scope="usa", hover_name='State',
                                color_continuous_scale='Blues', title="Sales Density by State")
        fig_map.update_layout(**get_plotly_theme(), height=500)
        st.plotly_chart(fig_map, use_container_width=True)
        
    with col2:
        st.subheader("🏙️ Top 5 Cities")
        city_data = df.groupby('City')['Sales'].sum().nlargest(5).reset_index()
        
        for _, row in city_data.iterrows():
            st.markdown(f"""
            <div class="metric-card" style="margin-bottom:10px; padding:15px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-weight:bold; font-size:1.1rem;">{row['City']}</span>
                    <span style="color:#38bdf8; font-weight:bold;">${row['Sales']:,.0f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

def render_download(df):
    st.markdown("---")
    col1, col2, col3 = st.columns([2, 2, 2])
    with col2:
        csv = df.to_csv(index=False)
        st.download_button(label="📥 Download Filtered Data (CSV)", data=csv,
            file_name=f"superstore_sales_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv", use_container_width=True)

# ── Main Application ──────────────────────────────────────────────────────────

def main():
    df = load_data()
    if df.empty:
        st.stop()

    nav_selection, date_range, regions, categories, segments = render_sidebar(df)
    filtered_df = apply_filters(df, date_range, regions, categories, segments)

    if filtered_df.empty:
        st.warning("⚠️ No data matches your filters. Please reset filters.")
        st.stop()

    if nav_selection == "Overview":
        render_overview(filtered_df)
    elif nav_selection == "Sales Analysis":
        render_sales_analysis(filtered_df)
    elif nav_selection == "Product Insights":
        render_product_insights(filtered_df)
    elif nav_selection == "Customer Intelligence":
        render_customer_intelligence(filtered_df)
    elif nav_selection == "Geographic Map":
        render_geographic_map(filtered_df)

    render_download(filtered_df)
    
    st.markdown("---")
    st.markdown('<div style="text-align:center;color:#718096;font-size:0.8rem;padding:20px;">📊 Superstore Analytics Pro • Built with Streamlit</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
