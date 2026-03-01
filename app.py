import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="Superstore Analytics Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Minimal CSS
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0a0f1c 0%, #1a1f2f 100%);
    }
    .metric-card {
        background: rgba(30, 41, 59, 0.8);
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
    }
    .metric-label { color: #94a3b8; font-size: 0.9rem; }
    .metric-value { color: #f1f5f9; font-size: 2rem; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
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
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

def format_currency(value):
    if value >= 1e6:
        return f"${value/1e6:.1f}M"
    elif value >= 1e3:
        return f"${value/1e3:.1f}K"
    else:
        return f"${value:,.0f}"

# Main app
def main():
    # Load data
    df = load_data()
    if df.empty:
        st.stop()
    
    # Sidebar
    with st.sidebar:
        st.title("📊 Analytics Pro")
        
        # Navigation
        page = st.radio(
            "Navigate",
            ["Overview", "Sales Analysis", "Product Insights", "Customer Intelligence", "Maps"]
        )
        
        st.markdown("---")
        
        # Simple filters
        st.subheader("Filters")
        
        # Date range
        min_date = df['Order Date'].min()
        max_date = df['Order Date'].max()
        date_range = st.date_input(
            "Date Range",
            value=[min_date, max_date],
            min_value=min_date,
            max_value=max_date
        )
        
        # Category filter
        categories = st.multiselect(
            "Categories",
            options=sorted(df['Category'].unique()),
            default=[]
        )
    
    # Apply filters
    filtered_df = df.copy()
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = filtered_df[
            (filtered_df['Order Date'] >= pd.Timestamp(start_date)) & 
            (filtered_df['Order Date'] <= pd.Timestamp(end_date))
        ]
    
    if categories:
        filtered_df = filtered_df[filtered_df['Category'].isin(categories)]
    
    # Show record count
    st.caption(f"Showing {len(filtered_df):,} records")
    
    # Page routing
    if page == "Overview":
        show_overview(filtered_df)
    elif page == "Sales Analysis":
        show_sales_analysis(filtered_df)
    elif page == "Product Insights":
        show_product_insights(filtered_df)
    elif page == "Customer Intelligence":
        show_customer_intelligence(filtered_df)
    elif page == "Maps":
        show_maps(filtered_df)

def show_overview(df):
    st.title("📊 Executive Overview")
    
    # Simple metrics
    total_sales = df['Sales'].sum()
    total_profit = df['Profit'].sum()
    total_orders = df['Order ID'].nunique()
    avg_shipping = df['Shipping_Days'].mean()
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Revenue</div>
            <div class="metric-value">{format_currency(total_sales)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Profit</div>
            <div class="metric-value">{format_currency(total_profit)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Orders</div>
            <div class="metric-value">{total_orders:,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Avg Shipping</div>
            <div class="metric-value">{avg_shipping:.1f} days</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Simple charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Sales Trend")
        
        # Simple line chart
        daily_sales = df.groupby(df['Order Date'].dt.date)['Sales'].sum().reset_index()
        daily_sales.columns = ['Date', 'Sales']
        
        fig = px.line(daily_sales, x='Date', y='Sales', title="Daily Sales")
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Sales by Category")
        
        cat_sales = df.groupby('Category')['Sales'].sum().reset_index()
        
        fig = px.pie(cat_sales, values='Sales', names='Category', title="Category Distribution")
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

def show_sales_analysis(df):
    st.title("📈 Sales Analysis")
    
    # Simple tab layout
    tab1, tab2 = st.tabs(["Time Analysis", "Segment Analysis"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Monthly Sales")
            monthly = df.groupby(df['Order Date'].dt.to_period('M').astype(str))['Sales'].sum().reset_index()
            monthly.columns = ['Month', 'Sales']
            
            fig = px.bar(monthly, x='Month', y='Sales', title="Monthly Sales")
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Sales by Day of Week")
            dow = df.groupby('DayOfWeek')['Sales'].mean().reset_index()
            
            fig = px.bar(dow, x='DayOfWeek', y='Sales', title="Average Sales by Day")
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Sales by Segment")
            seg = df.groupby('Segment')['Sales'].sum().reset_index()
            
            fig = px.bar(seg, x='Segment', y='Sales', title="Sales by Segment")
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Sales by Ship Mode")
            ship = df.groupby('Ship Mode')['Sales'].sum().reset_index()
            
            fig = px.pie(ship, values='Sales', names='Ship Mode', title="Sales by Shipping")
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)

def show_product_insights(df):
    st.title("📦 Product Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top Sub-Categories by Sales")
        top_subcat = df.groupby('Sub-Category')['Sales'].sum().nlargest(10).reset_index()
        
        fig = px.bar(top_subcat, x='Sales', y='Sub-Category', orientation='h', title="Top 10 Sub-Categories")
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Profit by Category")
        cat_profit = df.groupby('Category')['Profit'].sum().reset_index()
        
        fig = px.bar(cat_profit, x='Category', y='Profit', title="Profit by Category")
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)

def show_customer_intelligence(df):
    st.title("👥 Customer Intelligence")
    
    # Simple customer metrics
    total_customers = df['Customer ID'].nunique()
    avg_sale_per_customer = df.groupby('Customer ID')['Sales'].sum().mean()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Customers</div>
            <div class="metric-value">{total_customers:,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Avg Spend per Customer</div>
            <div class="metric-value">{format_currency(avg_sale_per_customer)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Customer purchase frequency
    st.subheader("Customer Purchase Frequency")
    cust_orders = df.groupby('Customer ID')['Order ID'].nunique().value_counts().reset_index()
    cust_orders.columns = ['Orders', 'Customers']
    
    fig = px.bar(cust_orders, x='Orders', y='Customers', title="Order Frequency Distribution")
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

def show_maps(df):
    st.title("🗺️ Geographic Analysis")
    
    # Simple state-level aggregation
    state_data = df.groupby('State')['Sales'].sum().reset_index()
    state_data = state_data.nlargest(10, 'Sales')
    
    fig = px.bar(state_data, x='Sales', y='State', orientation='h', title="Top 10 States by Sales")
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # City level
    st.subheader("Top Cities")
    city_data = df.groupby('City')['Sales'].sum().nlargest(10).reset_index()
    
    fig = px.bar(city_data, x='Sales', y='City', orientation='h', title="Top 10 Cities")
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
