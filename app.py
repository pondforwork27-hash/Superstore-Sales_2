import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import warnings
import pytz

# Ignore warnings for cleaner output
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
    /* Global Background */
    .stApp {
        background: linear-gradient(135deg, #0a0f1c 0%, #1a1f2f 100%);
        color: #e2e8f0;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Cards */
    .metric-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.9));
        backdrop-filter: blur(10px);
        border: 1px solid rgba(56, 189, 248, 0.1);
        border-radius: 16px;
        padding: 24px;
        transition: all 0.3s ease;
        box-shadow: 0 8px 32px -6px rgba(0, 0, 0, 0.4);
        height: 100%;
        position: relative;
        overflow: hidden;
    }
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #38bdf8, #8b5cf6);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-4px);
        border-color: #38bdf8;
        box-shadow: 0 20px 40px -12px rgba(56, 189, 248, 0.3);
    }
    .metric-card:hover::before {
        opacity: 1;
    }
    .metric-label { 
        font-size: 0.85rem; 
        color: #94a3b8; 
        text-transform: uppercase; 
        letter-spacing: 0.1em; 
        font-weight: 600;
        margin-bottom: 8px;
    }
    .metric-value { 
        font-size: 2.2rem; 
        font-weight: 700; 
        color: #f1f5f9; 
        line-height: 1.2;
        margin-bottom: 8px;
    }
    .metric-delta { 
        font-size: 0.85rem; 
        color: #4ade80; 
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 4px;
    }
    .metric-delta.neg { color: #f87171; }

    /* Insight Cards */
    .insight-box {
        background: rgba(15, 23, 42, 0.7);
        backdrop-filter: blur(5px);
        border-left: 4px solid #38bdf8;
        padding: 16px 20px;
        border-radius: 12px;
        margin-bottom: 16px;
        transition: transform 0.2s ease;
    }
    .insight-box:hover {
        transform: translateX(4px);
    }
    .insight-box.warn { border-left-color: #fbbf24; }
    .insight-box.danger { border-left-color: #f87171; }
    .insight-box.good { border-left-color: #4ade80; }
    
    /* Revenue Intelligence Card */
    .revenue-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.95));
        border: 1px solid rgba(139, 92, 246, 0.3);
        border-radius: 20px;
        padding: 24px;
        margin-top: 20px;
        box-shadow: 0 20px 40px -12px rgba(139, 92, 246, 0.3);
        position: relative;
        overflow: hidden;
    }
    .revenue-card::after {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(139, 92, 246, 0.1) 0%, transparent 70%);
        animation: pulse 8s ease infinite;
    }
    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 0.5; }
        50% { transform: scale(1.2); opacity: 0.2; }
    }
    .revenue-header {
        color: #c4b5fd;
        font-size: 1rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        margin-bottom: 20px;
        border-bottom: 1px solid rgba(139, 92, 246, 0.2);
        padding-bottom: 12px;
        position: relative;
        z-index: 1;
    }
    
    /* Navigation */
    .nav-item {
        padding: 12px 16px;
        margin: 4px 0;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.2s ease;
        color: #94a3b8;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .nav-item:hover {
        background: rgba(56, 189, 248, 0.1);
        color: #38bdf8;
    }
    .nav-item.active {
        background: #1e293b;
        color: #38bdf8;
        border-left: 3px solid #38bdf8;
    }
    
    /* Table Styling */
    .dataframe {
        background: rgba(15, 23, 42, 0.6) !important;
        border-radius: 12px !important;
        overflow: hidden;
    }
    
    /* Progress Bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #38bdf8, #8b5cf6) !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(15, 23, 42, 0.6);
        padding: 8px;
        border-radius: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 16px;
        background: transparent;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(56, 189, 248, 0.2) !important;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar { width: 10px; height: 10px; }
    ::-webkit-scrollbar-track { background: #0f172a; border-radius: 5px; }
    ::-webkit-scrollbar-thumb { 
        background: linear-gradient(135deg, #334155, #475569);
        border-radius: 5px; 
        border: 2px solid #0f172a;
    }
    ::-webkit-scrollbar-thumb:hover { background: #5b6b84; }
    
    /* Loading Animation */
    .loading-spinner {
        border: 3px solid rgba(56, 189, 248, 0.1);
        border-top-color: #38bdf8;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
    }
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
</style>
""", unsafe_allow_html=True)

# ── Helper Functions ──────────────────────────────────────────────────────────

@st.cache_data(ttl=3600, show_spinner="Loading data...")
def load_data():
    try:
        # Ensure this file exists in your directory
        df = pd.read_csv('cleaned_train.csv')
        
        # Ensure date columns are datetime
        df['Order Date'] = pd.to_datetime(df['Order Date'])
        df['Ship Date'] = pd.to_datetime(df['Ship Date'])
        
        # Feature Engineering
        df['Year'] = df['Order Date'].dt.year
        df['Month'] = df['Order Date'].dt.month
        df['Month_Name'] = df['Order Date'].dt.month_name()
        df['DayOfWeek'] = df['Order Date'].dt.day_name()
        df['Quarter'] = df['Order Date'].dt.quarter
        df['Year_Quarter'] = 'Q' + df['Quarter'].astype(str) + ' ' + df['Year'].astype(str)
        df['Shipping_Days'] = (df['Ship Date'] - df['Order Date']).dt.days
        
        # Check for Profit column (Standard Superstore dataset has it)
        if 'Profit' not in df.columns:
            # Fallback simulation if missing
            df['Profit'] = df['Sales'] * 0.25 
            df['Profit Margin'] = 25.0
        else:
            df['Profit Margin'] = (df['Profit'] / df['Sales']) * 100
        
        # State Abbreviations
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
        
        # Add time-based features for forecasting
        df['Order_Timestamp'] = df['Order Date'].astype(np.int64) // 10**9
        df['DayOfWeek_Num'] = df['Order Date'].dt.dayofweek
        df['Is_Weekend'] = df['DayOfWeek_Num'].isin([5, 6]).astype(int)
        
        return df
    except Exception as e:
        st.error(f"🚨 Critical Error Loading Data: {e}")
        return pd.DataFrame()

def get_plotly_theme():
    return {
        'layout': {
            'font': {'color': '#e2e8f0', 'family': 'Inter, -apple-system, BlinkMacSystemFont, sans-serif'},
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'paper_bgcolor': 'rgba(0,0,0,0)',
            'xaxis': {
                'gridcolor': '#1e293b',
                'linecolor': '#334155',
                'tickcolor': '#475569',
                'title_font': {'size': 12},
                'tickfont': {'size': 11}
            },
            'yaxis': {
                'gridcolor': '#1e293b',
                'linecolor': '#334155',
                'tickcolor': '#475569',
                'title_font': {'size': 12},
                'tickfont': {'size': 11}
            },
            'hovermode': 'x unified',
            'hoverlabel': {
                'bgcolor': '#1e293b',
                'font_color': '#f8fafc',
                'bordercolor': '#38bdf8',
                'font_size': 12
            },
            'legend': {
                'font': {'color': '#94a3b8'},
                'bgcolor': 'rgba(15, 23, 42, 0.6)',
                'bordercolor': '#334155',
                'borderwidth': 1
            },
            'margin': {'l': 40, 'r': 40, 't': 40, 'b': 40}
        }
    }

def format_currency(value):
    """Format currency values"""
    if value >= 1e6:
        return f"${value/1e6:.1f}M"
    elif value >= 1e3:
        return f"${value/1e3:.1f}K"
    else:
        return f"${value:,.0f}"

def calculate_growth(current, previous):
    """Calculate growth percentage"""
    if previous == 0:
        return 0
    return ((current - previous) / previous) * 100

# ── Navigation Function ───────────────────────────────────────────────────────

def render_navigation():
    """Render navigation using native Streamlit components"""
    st.sidebar.markdown("""
    <div style="text-align: center; margin-bottom: 30px;">
        <h1 style="color: #38bdf8; font-size: 2rem; margin-bottom: 0;">📊</h1>
        <h2 style="color: #f1f5f9; font-size: 1.5rem; margin-top: 0;">Analytics Pro</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation using radio buttons with custom styling
    nav_options = {
        "Overview": "🏠 Overview",
        "Sales Analysis": "📈 Sales Analysis",
        "Product Insights": "📦 Product Insights",
        "Customer Intelligence": "👥 Customer Intelligence",
        "Geographic Map": "🗺️ Geographic Map"
    }
    
    # Create a list of display names
    display_names = list(nav_options.values())
    
    # Use radio for navigation
    selected_display = st.sidebar.radio(
        "Navigation",
        options=display_names,
        label_visibility="collapsed"
    )
    
    # Map back to internal names
    for key, value in nav_options.items():
        if value == selected_display:
            return key
    
    return "Overview"

# ── Render Functions ──────────────────────────────────────────────────────────

def render_sidebar_filters(df):
    """Render filters in sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔍 Filter Panel")
    
    # Date range with quick selects
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("📅 This Year", use_container_width=True):
            current_year = datetime.now().year
            date_range = [datetime(current_year, 1, 1), datetime(current_year, 12, 31)]
    with col2:
        if st.button("📅 Last Year", use_container_width=True):
            current_year = datetime.now().year
            date_range = [datetime(current_year-1, 1, 1), datetime(current_year-1, 12, 31)]
    
    min_date = df['Order Date'].min()
    max_date = df['Order Date'].max()
    
    date_range = st.sidebar.date_input(
        "Custom Range",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )
    
    # Hierarchical filters
    with st.sidebar.expander("🏷️ Category Filters", expanded=True):
        all_categories = st.checkbox("Select All Categories", value=True)
        if all_categories:
            categories = []
        else:
            categories = st.multiselect(
                "Categories",
                options=sorted(df['Category'].unique()),
                default=[]
            )
    
    with st.sidebar.expander("📍 Region Filters", expanded=True):
        all_regions = st.checkbox("Select All Regions", value=True)
        if all_regions:
            regions = []
        else:
            regions = st.multiselect(
                "Regions",
                options=sorted(df['Region'].unique()),
                default=[]
            )
    
    with st.sidebar.expander("👥 Segment Filters", expanded=True):
        all_segments = st.checkbox("Select All Segments", value=True)
        if all_segments:
            segments = []
        else:
            segments = st.multiselect(
                "Segments",
                options=sorted(df['Segment'].unique()),
                default=[]
            )
    
    # Search box
    with st.sidebar.expander("🔎 Search", expanded=False):
        search_term = st.text_input("Search by Product or Customer", "")
    
    # Reset filters button
    if st.sidebar.button("🔄 Reset All Filters", use_container_width=True):
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # Data summary
    st.sidebar.markdown("### 📊 Data Summary")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.metric("Total Records", f"{len(df):,}")
    with col2:
        st.metric("Date Range", f"{df['Order Date'].min().year}-{df['Order Date'].max().year}")
    
    st.sidebar.markdown("---")
    st.sidebar.caption(f"⚡ Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    st.sidebar.caption("📁 Source: cleaned_train.csv")
    
    return date_range, regions, categories, segments, search_term

def apply_filters(df, date_range, regions, categories, segments, search_term):
    mask = pd.Series([True] * len(df))
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        mask &= (df['Order Date'] >= pd.Timestamp(start_date)) & (df['Order Date'] <= pd.Timestamp(end_date))
    
    if regions: 
        mask &= df['Region'].isin(regions)
    if categories: 
        mask &= df['Category'].isin(categories)
    if segments: 
        mask &= df['Segment'].isin(segments)
    
    if search_term:
        # Check if columns exist before searching
        if 'Product Name' in df.columns:
            mask &= df['Product Name'].str.contains(search_term, case=False, na=False)
        if 'Customer Name' in df.columns:
            mask &= df['Customer Name'].str.contains(search_term, case=False, na=False)
    
    return df[mask].copy()

def render_revenue_intelligence(df):
    """Enhanced revenue intelligence with more insights"""
    subcat_stats = df.groupby('Sub-Category').agg({
        'Sales': 'sum', 
        'Profit': 'sum',
        'Order ID': 'nunique',
        'Quantity': 'sum'
    }).reset_index()
    
    if subcat_stats.empty:
        return

    subcat_stats['Avg Order Value'] = subcat_stats['Sales'] / subcat_stats['Order ID']
    subcat_stats['Profit Margin'] = (subcat_stats['Profit'] / subcat_stats['Sales']) * 100
    
    top_revenue = subcat_stats.nlargest(1, 'Sales').iloc[0]
    top_profit = subcat_stats.nlargest(1, 'Profit').iloc[0]
    top_volume = subcat_stats.nlargest(1, 'Order ID').iloc[0]
    
    # Create columns for insights
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style="background: rgba(56, 189, 248, 0.1); padding: 15px; border-radius: 12px; text-align: center;">
            <div style="color: #7dd3fc; font-size: 0.8rem; text-transform: uppercase;">Top Revenue</div>
            <div style="color: #fff; font-size: 1.3rem; font-weight: bold;">{top_revenue['Sub-Category']}</div>
            <div style="color: #94a3b8; font-size: 0.9rem;">{format_currency(top_revenue['Sales'])}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        margin_color = "#4ade80" if top_profit['Profit Margin'] > 20 else "#fbbf24"
        st.markdown(f"""
        <div style="background: rgba(74, 222, 128, 0.1); padding: 15px; border-radius: 12px; text-align: center;">
            <div style="color: {margin_color}; font-size: 0.8rem; text-transform: uppercase;">Most Profitable</div>
            <div style="color: #fff; font-size: 1.3rem; font-weight: bold;">{top_profit['Sub-Category']}</div>
            <div style="color: #94a3b8; font-size: 0.9rem;">{top_profit['Profit Margin']:.1f}% Margin</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="background: rgba(168, 85, 247, 0.1); padding: 15px; border-radius: 12px; text-align: center;">
            <div style="color: #c4b5fd; font-size: 0.8rem; text-transform: uppercase;">Highest Volume</div>
            <div style="color: #fff; font-size: 1.3rem; font-weight: bold;">{top_volume['Sub-Category']}</div>
            <div style="color: #94a3b8; font-size: 0.9rem;">{top_volume['Order ID']:,.0f} Orders</div>
        </div>
        """, unsafe_allow_html=True)

def render_overview(df):
    st.title("📊 Executive Dashboard")
    
    # Date context
    current_date = df['Order Date'].max()
    previous_period_start = current_date - timedelta(days=365)
    
    # Filter data for current and previous periods
    current_data = df[df['Order Date'] > previous_period_start]
    previous_data = df[(df['Order Date'] <= previous_period_start) & 
                       (df['Order Date'] > (previous_period_start - timedelta(days=365)))]
    
    # KPIs with growth
    total_sales = current_data['Sales'].sum()
    prev_sales = previous_data['Sales'].sum()
    sales_growth = calculate_growth(total_sales, prev_sales)
    
    total_profit = current_data['Profit'].sum()
    prev_profit = previous_data['Profit'].sum()
    profit_growth = calculate_growth(total_profit, prev_profit)
    
    total_orders = current_data['Order ID'].nunique()
    prev_orders = previous_data['Order ID'].nunique()
    orders_growth = calculate_growth(total_orders, prev_orders)
    
    avg_shipping = current_data['Shipping_Days'].mean()
    prev_shipping = previous_data['Shipping_Days'].mean()
    shipping_improvement = ((prev_shipping - avg_shipping) / prev_shipping) * 100 if prev_shipping > 0 else 0
    
    profit_margin = (total_profit / total_sales) * 100 if total_sales > 0 else 0
    
    # Metric row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        delta_color = "normal" if sales_growth >= 0 else "inverse"
        st.metric(
            "Total Revenue",
            format_currency(total_sales),
            delta=f"{sales_growth:+.1f}%",
            delta_color=delta_color
        )
        
    with col2:
        delta_color = "normal" if profit_growth >= 0 else "inverse"
        st.metric(
            "Net Profit",
            format_currency(total_profit),
            delta=f"{profit_growth:+.1f}%",
            delta_color=delta_color
        )
        
    with col3:
        delta_color = "normal" if orders_growth >= 0 else "inverse"
        st.metric(
            "Total Orders",
            f"{total_orders:,}",
            delta=f"{orders_growth:+.1f}%",
            delta_color=delta_color
        )
        
    with col4:
        delta_color = "normal" if shipping_improvement >= 0 else "inverse"
        st.metric(
            "Avg Shipping",
            f"{avg_shipping:.1f} days",
            delta=f"{shipping_improvement:+.1f}%",
            delta_color=delta_color,
            help="Negative delta means faster shipping"
        )

    st.markdown("---")
    
    # Main Charts Row
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📈 Revenue Trend")
        
        # Multiple time aggregations
        time_period = st.radio(
            "View by:",
            ["Monthly", "Quarterly", "Yearly"],
            horizontal=True,
            key="time_period"
        )
        
        if time_period == "Monthly":
            time_group = df['Order Date'].dt.to_period('M')
        elif time_period == "Quarterly":
            time_group = df['Year_Quarter']
        else:
            time_group = df['Year']
            
        trend_data = df.groupby(time_group)['Sales'].agg(['sum', 'count', 'mean']).reset_index()
        trend_data.columns = ['Period', 'Total Sales', 'Order Count', 'Avg Order Value']
        
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=trend_data['Period'].astype(str),
            y=trend_data['Total Sales'],
            mode='lines+markers',
            name='Total Sales',
            line=dict(color='#38bdf8', width=3),
            marker=dict(size=8, color='#38bdf8', line=dict(color='#fff', width=2))
        ))
        fig_trend.add_trace(go.Bar(
            x=trend_data['Period'].astype(str),
            y=trend_data['Order Count'],
            name='Order Count',
            yaxis='y2',
            marker_color='rgba(139, 92, 246, 0.3)',
            marker_line_color='#8b5cf6',
            marker_line_width=1
        ))
        
        fig_trend.update_layout(
            **get_plotly_theme(),
            height=450,
            yaxis=dict(title='Total Sales ($)', titlefont=dict(color='#38bdf8')),
            yaxis2=dict(
                title='Order Count',
                titlefont=dict(color='#8b5cf6'),
                tickfont=dict(color='#8b5cf6'),
                overlaying='y',
                side='right'
            ),
            hovermode='x unified',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
        )
        
        st.plotly_chart(fig_trend, use_container_width=True)
        
    with col2:
        st.subheader("🏷️ Category Performance")
        
        cat_data = df.groupby('Category').agg({
            'Sales': 'sum',
            'Profit': 'sum'
        }).reset_index()
        
        fig_donut = go.Figure(data=[go.Pie(
            labels=cat_data['Category'],
            values=cat_data['Sales'],
            hole=.6,
            marker=dict(colors=['#38bdf8', '#8b5cf6', '#f97316']),
            textinfo='label+percent',
            textposition='outside',
            textfont=dict(color='#e2e8f0', size=12),
            hoverinfo='label+value+percent',
            hovertemplate='<b>%{label}</b><br>Sales: $%{value:,.0f}<br>Percent: %{percent}<extra></extra>'
        )])
        
        fig_donut.update_layout(
            **get_plotly_theme(),
            height=350,
            showlegend=False,
            annotations=[dict(
                text=f'Total<br>${cat_data["Sales"].sum():,.0f}',
                x=0.5, y=0.5,
                font=dict(size=14, color='#e2e8f0'),
                showarrow=False
            )]
        )
        
        st.plotly_chart(fig_donut, use_container_width=True)
        
        # Category metrics
        for _, row in cat_data.iterrows():
            margin = (row['Profit'] / row['Sales']) * 100
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; 
                        padding: 8px; margin: 4px 0; background: rgba(255,255,255,0.05); border-radius: 8px;">
                <span style="color: #94a3b8;">{row['Category']}</span>
                <span style="color: {'#4ade80' if margin > 15 else '#f87171'}; font-weight: 600;">
                    {margin:.1f}% margin
                </span>
            </div>
            """, unsafe_allow_html=True)

    # Revenue Intelligence Section
    st.markdown("### 💡 Strategic Insights")
    render_revenue_intelligence(df)

def render_sales_analysis(df):
    st.title("💰 Sales Analytics")
    
    tab1, tab2, tab3 = st.tabs(["📈 Time Series Analysis", "📊 Segment Analysis", "🚚 Shipping Analysis"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📅 Sales Heatmap")
            
            # Create pivot table for heatmap
            heatmap_data = df.pivot_table(
                values='Sales',
                index=df['Order Date'].dt.hour,
                columns=df['Order Date'].dt.dayofweek,
                aggfunc='mean',
                fill_value=0
            )
            
            day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            heatmap_data.columns = [day_names[i] for i in heatmap_data.columns]
            
            fig_heat = go.Figure(data=go.Heatmap(
                z=heatmap_data.values,
                x=heatmap_data.columns,
                y=heatmap_data.index,
                colorscale='Viridis',
                hoverongaps=False,
                hovertemplate='Day: %{x}<br>Hour: %{y}<br>Avg Sales: $%{z:,.0f}<extra></extra>'
            ))
            
            fig_heat.update_layout(
                **get_plotly_theme(),
                height=400,
                xaxis_title="Day of Week",
                yaxis_title="Hour of Day",
                yaxis=dict(autorange='reversed')
            )
            
            st.plotly_chart(fig_heat, use_container_width=True)
            
        with col2:
            st.subheader("📊 Sales Distribution")
            
            # Distribution by category over time
            category_trend = df.groupby([df['Order Date'].dt.to_period('M'), 'Category'])['Sales'].sum().reset_index()
            category_trend['Order Date'] = category_trend['Order Date'].dt.to_timestamp()
            
            fig_area = px.area(
                category_trend,
                x='Order Date',
                y='Sales',
                color='Category',
                title="Category Sales Trend"
            )
            
            fig_area.update_layout(
                **get_plotly_theme(),
                height=400,
                showlegend=True,
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
            )
            
            st.plotly_chart(fig_area, use_container_width=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("👥 Segment Performance")
            
            segment_data = df.groupby('Segment').agg({
                'Sales': ['sum', 'mean'],
                'Profit': 'sum',
                'Order ID': 'nunique'
            }).round(2)
            
            segment_data.columns = ['Total Sales', 'Avg Order Value', 'Total Profit', 'Order Count']
            segment_data = segment_data.reset_index()
            segment_data['Profit Margin'] = (segment_data['Total Profit'] / segment_data['Total Sales']) * 100
            
            fig_segment = go.Figure()
            fig_segment.add_trace(go.Bar(
                x=segment_data['Segment'],
                y=segment_data['Total Sales'],
                name='Total Sales',
                marker_color='#38bdf8',
                text=segment_data['Total Sales'].apply(lambda x: f'${x/1000:.0f}K'),
                textposition='outside'
            ))
            
            fig_segment.add_trace(go.Scatter(
                x=segment_data['Segment'],
                y=segment_data['Profit Margin'],
                name='Profit Margin %',
                yaxis='y2',
                mode='lines+markers',
                line=dict(color='#4ade80', width=3),
                marker=dict(size=10, color='#4ade80'),
                text=segment_data['Profit Margin'].apply(lambda x: f'{x:.1f}%'),
                textposition='top center'
            ))
            
            fig_segment.update_layout(
                **get_plotly_theme(),
                height=400,
                yaxis=dict(title='Total Sales ($)', titlefont=dict(color='#38bdf8')),
                yaxis2=dict(
                    title='Profit Margin %',
                    titlefont=dict(color='#4ade80'),
                    tickfont=dict(color='#4ade80'),
                    overlaying='y',
                    side='right',
                    range=[0, max(segment_data['Profit Margin']) * 1.2]
                ),
                showlegend=True,
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
            )
            
            st.plotly_chart(fig_segment, use_container_width=True)
            
        with col2:
            st.subheader("📊 Correlation Matrix")
            
            # Select numeric columns for correlation
            numeric_cols = ['Sales', 'Profit', 'Quantity', 'Discount', 'Shipping_Days']
            corr_data = df[numeric_cols].corr()
            
            fig_corr = go.Figure(data=go.Heatmap(
                z=corr_data,
                x=corr_data.columns,
                y=corr_data.columns,
                colorscale='RdBu_r',
                zmin=-1, zmax=1,
                text=corr_data.round(2),
                texttemplate='%{text}',
                textfont={"color": "#e2e8f0"},
                hovertemplate='%{x} vs %{y}: %{z:.2f}<extra></extra>'
            ))
            
            fig_corr.update_layout(
                **get_plotly_theme(),
                height=400,
                title="Feature Correlation Analysis"
            )
            
            st.plotly_chart(fig_corr, use_container_width=True)
    
    with tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🚚 Shipping Mode Analysis")
            
            ship_data = df.groupby('Ship Mode').agg({
                'Shipping_Days': ['mean', 'min', 'max'],
                'Sales': 'sum',
                'Order ID': 'count'
            }).round(2)
            
            ship_data.columns = ['Avg Days', 'Min Days', 'Max Days', 'Total Sales', 'Order Count']
            ship_data = ship_data.reset_index()
            
            fig_ship = px.bar(
                ship_data,
                x='Ship Mode',
                y='Avg Days',
                color='Total Sales',
                text='Avg Days',
                title="Average Shipping Days by Mode",
                color_continuous_scale='Viridis',
                labels={'Avg Days': 'Average Shipping Days'}
            )
            
            fig_ship.update_traces(texttemplate='%{text:.1f} days', textposition='outside')
            fig_ship.update_layout(**get_plotly_theme(), height=400)
            
            st.plotly_chart(fig_ship, use_container_width=True)
            
        with col2:
            st.subheader("📦 Shipping Efficiency")
            
            # Calculate efficiency score
            ship_efficiency = df.groupby('Ship Mode').agg({
                'Shipping_Days': 'mean',
                'Sales': 'sum'
            }).reset_index()
            
            ship_efficiency['Efficiency Score'] = (
                ship_efficiency['Sales'] / ship_efficiency['Shipping_Days']
            ).round(0)
            
            fig_eff = px.scatter(
                ship_efficiency,
                x='Shipping_Days',
                y='Sales',
                size='Efficiency Score',
                color='Ship Mode',
                text='Ship Mode',
                title="Shipping Efficiency Matrix",
                size_max=60,
                labels={'Shipping_Days': 'Avg Shipping Days', 'Sales': 'Total Sales ($)'}
            )
            
            fig_eff.update_traces(textposition='top center')
            fig_eff.update_layout(**get_plotly_theme(), height=400)
            
            st.plotly_chart(fig_eff, use_container_width=True)

def render_product_insights(df):
    st.title("📦 Product Performance")
    
    # Top-level metrics
    total_products = df['Product ID'].nunique() if 'Product ID' in df.columns else 0
    avg_price = df['Sales'].sum() / df['Quantity'].sum() if 'Quantity' in df.columns else 0
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Unique Products", f"{total_products:,}")
    with col2:
        st.metric("Avg Selling Price", f"${avg_price:.2f}")
    with col3:
        st.metric("Total Categories", f"{df['Category'].nunique()}")
    with col4:
        st.metric("Total Sub-Categories", f"{df['Sub-Category'].nunique()}")
    
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["📊 Category Analysis", "🏆 Top Performers", "⚠️ Profitability Analysis"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Category Performance Matrix")
            
            cat_stats = df.groupby(['Category', 'Sub-Category']).agg({
                'Sales': 'sum',
                'Profit': 'sum',
                'Order ID': 'nunique',
                'Quantity': 'sum' if 'Quantity' in df.columns else 'count'
            }).reset_index()
            
            cat_stats['Profit Margin'] = (cat_stats['Profit'] / cat_stats['Sales']) * 100
            cat_stats['Avg Order Value'] = cat_stats['Sales'] / cat_stats['Order ID']
            
            fig_bubble = px.scatter(
                cat_stats,
                x='Sales',
                y='Profit Margin',
                size='Avg Order Value',
                color='Category',
                hover_name='Sub-Category',
                size_max=50,
                labels={'Sales': 'Total Sales ($)', 'Profit Margin': 'Profit Margin (%)'},
                title="Product Performance Matrix"
            )
            
            fig_bubble.add_hline(y=0, line_dash="dash", line_color="red", opacity=0.3)
            fig_bubble.add_vline(x=cat_stats['Sales'].median(), line_dash="dash", line_color="yellow", opacity=0.3)
            
            fig_bubble.update_layout(**get_plotly_theme(), height=500)
            st.plotly_chart(fig_bubble, use_container_width=True)
            
        with col2:
            st.subheader("Category Contribution")
            
            # Treemap
            cat_treemap = df.groupby(['Category', 'Sub-Category'])['Sales'].sum().reset_index()
            
            fig_treemap = px.treemap(
                cat_treemap,
                path=['Category', 'Sub-Category'],
                values='Sales',
                color='Sales',
                color_continuous_scale='Viridis',
                title="Sales Distribution by Category"
            )
            
            fig_treemap.update_layout(**get_plotly_theme(), height=500)
            st.plotly_chart(fig_treemap, use_container_width=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🏆 Top 10 Products by Sales")
            
            if 'Product Name' in df.columns:
                top_products = df.groupby('Product Name').agg({
                    'Sales': 'sum',
                    'Quantity': 'sum' if 'Quantity' in df.columns else 'count',
                    'Order ID': 'nunique'
                }).nlargest(10, 'Sales').reset_index()
                
                top_products['Avg Price'] = top_products['Sales'] / top_products['Quantity']
                
                fig_top = px.bar(
                    top_products,
                    x='Sales',
                    y='Product Name',
                    orientation='h',
                    color='Quantity',
                    text=top_products['Sales'].apply(lambda x: f'${x/1000:.0f}K'),
                    title="Top Products by Revenue",
                    color_continuous_scale='Viridis',
                    labels={'Sales': 'Total Sales ($)', 'Quantity': 'Units Sold'}
                )
                
                fig_top.update_layout(**get_plotly_theme(), height=500, yaxis={'categoryorder':'total ascending'})
                fig_top.update_traces(textposition='outside')
                st.plotly_chart(fig_top, use_container_width=True)
            else:
                st.info("Product Name column not available")
            
        with col2:
            st.subheader("📈 Top Sub-Categories by Growth")
            
            # Calculate growth (if we have multiple years)
            if df['Year'].nunique() > 1:
                latest_year = df['Year'].max()
                prev_year = latest_year - 1
                
                current = df[df['Year'] == latest_year].groupby('Sub-Category')['Sales'].sum()
                previous = df[df['Year'] == prev_year].groupby('Sub-Category')['Sales'].sum()
                
                growth_data = pd.DataFrame({
                    'Current': current,
                    'Previous': previous
                }).fillna(0)
                
                growth_data['Growth'] = ((growth_data['Current'] - growth_data['Previous']) / growth_data['Previous'].replace(0, np.nan)) * 100
                growth_data = growth_data.nlargest(10, 'Growth').reset_index()
                
                fig_growth = px.bar(
                    growth_data,
                    x='Growth',
                    y='Sub-Category',
                    orientation='h',
                    color='Growth',
                    color_continuous_scale='RdYlGn',
                    title="Top Growing Sub-Categories",
                    text=growth_data['Growth'].apply(lambda x: f'{x:.1f}%')
                )
                
                fig_growth.update_layout(**get_plotly_theme(), height=500)
                fig_growth.update_traces(textposition='outside')
                st.plotly_chart(fig_growth, use_container_width=True)
            else:
                st.info("Need multiple years of data for growth analysis")
    
    with tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("💰 Profit Margin Analysis")
            
            margin_data = df.groupby('Sub-Category')['Profit Margin'].mean().reset_index()
            margin_data = margin_data.sort_values('Profit Margin', ascending=False)
            
            colors = ['#4ade80' if x > 0 else '#f87171' for x in margin_data['Profit Margin']]
            
            fig_margin = px.bar(
                margin_data,
                x='Profit Margin',
                y='Sub-Category',
                orientation='h',
                title="Average Profit Margin by Sub-Category",
                color='Profit Margin',
                color_continuous_scale='RdYlGn',
                text=margin_data['Profit Margin'].apply(lambda x: f'{x:.1f}%')
            )
            
            fig_margin.update_layout(**get_plotly_theme(), height=500)
            fig_margin.update_traces(textposition='outside')
            fig_margin.add_vline(x=0, line_width=2, line_dash="dash", line_color="red")
            
            st.plotly_chart(fig_margin, use_container_width=True)
            
        with col2:
            st.subheader("⚠️ Loss-Making Products")
            
            loss_products = df[df['Profit'] < 0].groupby('Sub-Category').agg({
                'Profit': 'sum',
                'Sales': 'sum',
                'Order ID': 'count'
            }).round(2)
            
            loss_products = loss_products[loss_products['Profit'] < 0].sort_values('Profit')
            
            if not loss_products.empty:
                loss_products['Loss Margin'] = (loss_products['Profit'] / loss_products['Sales'] * 100).abs()
                
                fig_loss = px.bar(
                    loss_products.reset_index(),
                    x='Profit',
                    y='Sub-Category',
                    orientation='h',
                    color='Loss Margin',
                    color_continuous_scale='Reds',
                    title="Loss by Sub-Category",
                    text=loss_products['Profit'].apply(lambda x: f'${abs(x):,.0f}')
                )
                
                fig_loss.update_layout(**get_plotly_theme(), height=500)
                fig_loss.update_traces(textposition='outside')
                st.plotly_chart(fig_loss, use_container_width=True)
            else:
                st.success("🎉 No loss-making products found!")

def render_customer_intelligence(df):
    st.title("👥 Customer Analytics")
    
    # Customer metrics
    total_customers = df['Customer ID'].nunique() if 'Customer ID' in df.columns else 0
    avg_customer_value = df.groupby('Customer ID')['Sales'].sum().mean() if 'Customer ID' in df.columns else 0
    repeat_customers = df.groupby('Customer ID')['Order ID'].nunique() if 'Customer ID' in df.columns else pd.Series()
    repeat_rate = (repeat_customers[repeat_customers > 1].count() / total_customers * 100) if total_customers > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Customers", f"{total_customers:,}")
    with col2:
        st.metric("Avg Customer Value", f"${avg_customer_value:,.0f}")
    with col3:
        st.metric("Repeat Rate", f"{repeat_rate:.1f}%")
    with col4:
        st.metric("Avg Orders/Customer", f"{repeat_customers.mean():.1f}")
    
    st.markdown("---")
    
    # RFM Analysis
    st.subheader("🎯 RFM Customer Segmentation")
    
    with st.spinner("Calculating RFM scores..."):
        # Calculate RFM metrics
        current_date = df['Order Date'].max()
        
        rfm = df.groupby('Customer ID').agg({
            'Order Date': lambda x: (current_date - x.max()).days,
            'Order ID': 'count',
            'Sales': 'sum'
        }).reset_index()
        
        rfm.columns = ['Customer ID', 'Recency', 'Frequency', 'Monetary']
        
        # Create scores
        try:
            rfm['R_Score'] = pd.qcut(rfm['Recency'], 4, labels=[4, 3, 2, 1], duplicates='drop')
            rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 4, labels=[1, 2, 3, 4], duplicates='drop')
            rfm['M_Score'] = pd.qcut(rfm['Monetary'], 4, labels=[1, 2, 3, 4], duplicates='drop')
            
            # Convert scores to numeric
            for col in ['R_Score', 'F_Score', 'M_Score']:
                rfm[col] = pd.to_numeric(rfm[col])
            
            rfm['RFM_Score'] = rfm['R_Score'] + rfm['F_Score'] + rfm['M_Score']
            
            # Segment customers
            def segment_customer(row):
                if row['RFM_Score'] >= 10:
                    return 'Champions'
                elif row['RFM_Score'] >= 8:
                    return 'Loyal Customers'
                elif row['RFM_Score'] >= 6:
                    return 'Potential Loyalists'
                elif row['RFM_Score'] >= 4:
                    return 'At Risk'
                else:
                    return 'Lost'
            
            rfm['Segment'] = rfm.apply(segment_customer, axis=1)
            
            # Display RFM visualization
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # 3D Scatter plot of RFM
                fig_rfm = px.scatter_3d(
                    rfm,
                    x='Recency',
                    y='Frequency',
                    z='Monetary',
                    color='Segment',
                    hover_name='Customer ID',
                    title="RFM Analysis - 3D Customer Segmentation",
                    labels={'Recency': 'Days Since Last Purchase', 
                           'Frequency': 'Number of Orders',
                           'Monetary': 'Total Spend ($)'}
                )
                
                fig_rfm.update_layout(**get_plotly_theme(), height=600)
                st.plotly_chart(fig_rfm, use_container_width=True)
                
            with col2:
                st.subheader("Segment Distribution")
                
                seg_counts = rfm['Segment'].value_counts().reset_index()
                seg_counts.columns = ['Segment', 'Count']
                
                fig_seg = px.pie(
                    seg_counts,
                    values='Count',
                    names='Segment',
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                
                fig_seg.update_layout(**get_plotly_theme(), height=400)
                st.plotly_chart(fig_seg, use_container_width=True)
                
                # Segment characteristics
                st.subheader("Segment Characteristics")
                seg_stats = rfm.groupby('Segment').agg({
                    'Recency': 'mean',
                    'Frequency': 'mean',
                    'Monetary': 'mean',
                    'Customer ID': 'count'
                }).round(1)
                
                seg_stats.columns = ['Avg Recency', 'Avg Frequency', 'Avg Spend', 'Count']
                seg_stats = seg_stats.sort_values('Avg Spend', ascending=False)
                
                st.dataframe(
                    seg_stats.style.format({
                        'Avg Recency': '{:.0f} days',
                        'Avg Frequency': '{:.1f}',
                        'Avg Spend': '${:,.0f}',
                        'Count': '{:,.0f}'
                    }),
                    use_container_width=True
                )
        except Exception as e:
            st.warning(f"RFM Analysis could not be completed: {e}")
    
    st.markdown("---")
    
    # Top Customers
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👑 Top 10 Customers by Spend")
        
        if 'Customer Name' in df.columns:
            top_customers = df.groupby('Customer Name').agg({
                'Sales': 'sum',
                'Order ID': 'nunique',
                'Profit': 'sum'
            }).nlargest(10, 'Sales').reset_index()
            
            top_customers['Avg Order'] = top_customers['Sales'] / top_customers['Order ID']
            
            fig_top = go.Figure(data=[
                go.Bar(
                    name='Total Spend',
                    x=top_customers['Customer Name'],
                    y=top_customers['Sales'],
                    marker_color='#38bdf8',
                    text=top_customers['Sales'].apply(lambda x: f'${x:,.0f}'),
                    textposition='outside'
                ),
                go.Scatter(
                    name='Avg Order Value',
                    x=top_customers['Customer Name'],
                    y=top_customers['Avg Order'],
                    yaxis='y2',
                    mode='lines+markers',
                    line=dict(color='#f97316', width=3),
                    marker=dict(size=8),
                    text=top_customers['Avg Order'].apply(lambda x: f'${x:,.0f}')
                )
            ])
            
            fig_top.update_layout(
                **get_plotly_theme(),
                height=400,
                yaxis=dict(title='Total Spend ($)', titlefont=dict(color='#38bdf8')),
                yaxis2=dict(
                    title='Avg Order Value ($)',
                    titlefont=dict(color='#f97316'),
                    tickfont=dict(color='#f97316'),
                    overlaying='y',
                    side='right'
                ),
                showlegend=True,
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
            )
            
            st.plotly_chart(fig_top, use_container_width=True)
        else:
            st.info("Customer Name column not available")
    
    with col2:
        st.subheader("📊 Customer Purchase Patterns")
        
        # Purchase frequency distribution
        freq_dist = df.groupby('Customer ID')['Order ID'].nunique().value_counts().reset_index()
        freq_dist.columns = ['Orders', 'Customer Count']
        freq_dist = freq_dist.sort_values('Orders')
        
        fig_freq = px.bar(
            freq_dist,
            x='Orders',
            y='Customer Count',
            title="Customer Purchase Frequency",
            labels={'Orders': 'Number of Orders', 'Customer Count': 'Number of Customers'},
            text='Customer Count'
        )
        
        fig_freq.update_layout(**get_plotly_theme(), height=400)
        fig_freq.update_traces(textposition='outside')
        
        st.plotly_chart(fig_freq, use_container_width=True)

def render_geographic_map(df):
    st.title("🌍 Geographic Analytics")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Map view selector
        map_metric = st.radio(
            "Color Map By:",
            ["Sales", "Profit", "Order Count"],
            horizontal=True
        )
        
        # Aggregate by state
        if map_metric == "Sales":
            state_data = df.groupby(['State', 'State Code'])['Sales'].sum().reset_index()
            color_metric = 'Sales'
            title = "Sales Distribution by State"
        elif map_metric == "Profit":
            state_data = df.groupby(['State', 'State Code'])['Profit'].sum().reset_index()
            color_metric = 'Profit'
            title = "Profit Distribution by State"
        else:
            state_data = df.groupby(['State', 'State Code'])['Order ID'].nunique().reset_index()
            state_data.columns = ['State', 'State Code', 'Order Count']
            color_metric = 'Order Count'
            title = "Order Volume by State"
        
        fig_map = px.choropleth(
            state_data,
            locations='State Code',
            locationmode="USA-states",
            color=color_metric,
            scope="usa",
            hover_name='State',
            color_continuous_scale='Viridis',
            title=title,
            labels={color_metric: map_metric}
        )
        
        fig_map.update_layout(
            **get_plotly_theme(),
            height=500,
            geo=dict(
                scope='usa',
                projection=go.layout.geo.Projection(type='albers usa'),
                showlakes=True,
                lakecolor='rgba(0,0,0,0)',
                landcolor='rgba(15, 23, 42, 0.8)'
            )
        )
        
        st.plotly_chart(fig_map, use_container_width=True)
        
    with col2:
        st.subheader("📍 Top States")
        
        top_states = state_data.nlargest(5, color_metric).reset_index(drop=True)
        
        for idx, row in top_states.iterrows():
            st.markdown(f"""
            <div class="metric-card" style="margin-bottom:10px; padding:15px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <span style="font-weight:bold; font-size:1.1rem;">{row['State']}</span>
                        <span style="color:#94a3b8; font-size:0.9rem; margin-left:8px;">#{idx+1}</span>
                    </div>
                    <span style="color:#38bdf8; font-weight:bold;">
                        {format_currency(row[color_metric]) if color_metric in ['Sales', 'Profit'] else f'{row[color_metric]:,.0f}'}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # City-level analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏙️ Top Cities by Sales")
        
        city_data = df.groupby('City').agg({
            'Sales': 'sum',
            'Profit': 'sum',
            'Order ID': 'nunique'
        }).nlargest(10, 'Sales').reset_index()
        
        city_data['Margin'] = (city_data['Profit'] / city_data['Sales'] * 100).round(1)
        
        fig_cities = px.bar(
            city_data,
            x='Sales',
            y='City',
            orientation='h',
            color='Margin',
            color_continuous_scale='RdYlGn',
            text=city_data['Sales'].apply(lambda x: f'${x/1000:.0f}K'),
            title="Top 10 Cities by Revenue"
        )
        
        fig_cities.update_layout(**get_plotly_theme(), height=500)
        fig_cities.update_traces(textposition='outside')
        
        st.plotly_chart(fig_cities, use_container_width=True)
    
    with col2:
        st.subheader("📊 Regional Performance")
        
        region_data = df.groupby('Region').agg({
            'Sales': 'sum',
            'Profit': 'sum',
            'Order ID': 'nunique',
            'State': 'nunique'
        }).reset_index()
        
        region_data['Margin'] = (region_data['Profit'] / region_data['Sales'] * 100).round(1)
        
        fig_region = go.Figure()
        
        fig_region.add_trace(go.Bar(
            name='Sales',
            x=region_data['Region'],
            y=region_data['Sales'],
            marker_color='#38bdf8',
            text=region_data['Sales'].apply(lambda x: f'${x/1000:.0f}K'),
            textposition='outside'
        ))
        
        fig_region.add_trace(go.Scatter(
            name='Margin %',
            x=region_data['Region'],
            y=region_data['Margin'],
            yaxis='y2',
            mode='lines+markers',
            line=dict(color='#4ade80', width=3),
            marker=dict(size=10, color='#4ade80'),
            text=region_data['Margin'].apply(lambda x: f'{x:.1f}%'),
            textposition='top center'
        ))
        
        fig_region.update_layout(
            **get_plotly_theme(),
            height=500,
            yaxis=dict(title='Total Sales ($)', titlefont=dict(color='#38bdf8')),
            yaxis2=dict(
                title='Profit Margin %',
                titlefont=dict(color='#4ade80'),
                tickfont=dict(color='#4ade80'),
                overlaying='y',
                side='right',
                range=[0, max(region_data['Margin']) * 1.2]
            ),
            showlegend=True,
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
        )
        
        st.plotly_chart(fig_region, use_container_width=True)

def render_export_options(df):
    """Enhanced export functionality"""
    st.markdown("---")
    
    with st.expander("📤 Export Options", expanded=False):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Full data export
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Full Data (CSV)",
                data=csv,
                file_name=f"superstore_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            # Summary export
            summary = pd.DataFrame({
                'Metric': ['Total Sales', 'Total Profit', 'Total Orders', 'Avg Order Value', 'Profit Margin'],
                'Value': [
                    df['Sales'].sum(),
                    df['Profit'].sum(),
                    df['Order ID'].nunique(),
                    df['Sales'].mean(),
                    (df['Profit'].sum() / df['Sales'].sum() * 100) if df['Sales'].sum() > 0 else 0
                ]
            })
            summary_csv = summary.to_csv(index=False)
            st.download_button(
                label="📊 Summary (CSV)",
                data=summary_csv,
                file_name=f"superstore_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col3:
            # Excel export (requires openpyxl)
            try:
                import io
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='Data', index=False)
                    
                    # Add summary sheet
                    summary.to_excel(writer, sheet_name='Summary', index=False)
                
                st.download_button(
                    label="📗 Excel Report",
                    data=buffer.getvalue(),
                    file_name=f"superstore_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            except:
                st.button("📗 Excel (Install openpyxl)", disabled=True, use_container_width=True)
        
        with col4:
            # JSON export
            json_str = df.to_json(orient='records', date_format='iso')
            st.download_button(
                label="📋 JSON Export",
                data=json_str,
                file_name=f"superstore_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )

# ── Main Application ──────────────────────────────────────────────────────────

def main():
    # Load Data
    with st.spinner("Loading data..."):
        df = load_data()
        if df.empty:
            st.error("Failed to load data. Please check the data file.")
            st.stop()

    # Render navigation in sidebar
    nav_selection = render_navigation()
    
    # Render filters in sidebar
    date_range, regions, categories, segments, search_term = render_sidebar_filters(df)
    
    # Apply filters
    filtered_df = apply_filters(df, date_range, regions, categories, segments, search_term)

    if filtered_df.empty:
        st.warning("⚠️ No data matches your filters. Please adjust your filters.")
        if st.button("Reset Filters"):
            st.rerun()
        st.stop()
    
    # Display filter summary
    with st.container():
        st.markdown(f"""
        <div style="background: rgba(56, 189, 248, 0.1); padding: 10px 20px; border-radius: 12px; margin-bottom: 20px;">
            <span style="color: #94a3b8;">Showing </span>
            <span style="color: #38bdf8; font-weight: 600;">{len(filtered_df):,}</span>
            <span style="color: #94a3b8;"> records from </span>
            <span style="color: #38bdf8;">{filtered_df['Order Date'].min().strftime('%Y-%m-%d')}</span>
            <span style="color: #94a3b8;"> to </span>
            <span style="color: #38bdf8;">{filtered_df['Order Date'].max().strftime('%Y-%m-%d')}</span>
        </div>
        """, unsafe_allow_html=True)

    # ── Render Content Based on Navigation ────────────────────────────────────
    
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

    # Export Options
    render_export_options(filtered_df)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align:center; padding: 20px;">
        <span style="color:#4b5563;">📊 Superstore Analytics Pro v2.0</span>
        <span style="color:#374151; margin:0 10px;">•</span>
        <span style="color:#4b5563;">Built with </span>
        <span style="color:#ef4444;">❤️</span>
        <span style="color:#4b5563;"> using Streamlit</span>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
