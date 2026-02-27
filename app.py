# ── Product Analysis ────────────────────────────────────────────────────────
st.header("📦 Product Analysis")

col1, col2 = st.columns(2)

with col1:
    # Product sub-category performance scatter plot with correct hover formatting
    subcat_stats = filtered_df.groupby('Sub-Category').agg({
        'Sales': 'sum',
        'Order ID': 'nunique'
    }).reset_index()
    subcat_stats['Avg Order Value'] = subcat_stats['Sales'] / subcat_stats['Order ID']
    subcat_stats = subcat_stats.sort_values('Sales', ascending=False).head(15)
    
    # Create a simple scatter plot with correct hover formatting
    fig_subcat_perf = px.scatter(
        subcat_stats,
        x='Order ID',
        y='Sales',
        size='Avg Order Value',
        color='Sub-Category',
        title='Sub-Category Performance (Top 15)',
        hover_name='Sub-Category',
        labels={
            'Order ID': 'Number of Orders',
            'Sales': 'Total Sales ($)',
            'Avg Order Value': 'Average Order Value ($)'
        },
        size_max=30
    )
    
    # Update hover template to show proper formatting with commas and 2 decimals
    fig_subcat_perf.update_traces(
        marker=dict(line=dict(width=1, color='white')),
        hovertemplate='<b>%{hovertext}</b><br>' +
                     'Sales: $%{y:,.2f}<br>' +
                     'Orders: %{x:,.0f}<br>' +
                     'Avg Order: $%{marker.size:,.2f}<extra></extra>'
    )
    
    fig_subcat_perf.update_layout(
        height=500,
        xaxis_title='Number of Orders',
        yaxis_title='Total Sales ($)',
        hoverlabel=dict(
            bgcolor='#0d1b2a',
            font_size=12,
            font_color='white'
        )
    )
    st.plotly_chart(fig_subcat_perf, use_container_width=True)

with col2:
    # Segment Correlation Analysis
    # Create monthly sales for each segment
    monthly_segment = filtered_df.groupby(['Year', 'Month', 'Segment'])['Sales'].sum().reset_index()
    monthly_segment['Date'] = pd.to_datetime(monthly_segment[['Year', 'Month']].assign(day=1))
    
    # Pivot for correlation
    segment_pivot = monthly_segment.pivot(index='Date', columns='Segment', values='Sales').fillna(0)
    segment_corr = segment_pivot.corr()
    
    # Create correlation heatmap
    fig_seg_corr = go.Figure(data=go.Heatmap(
        z=segment_corr.values,
        x=segment_corr.columns,
        y=segment_corr.index,
        colorscale=[[0, '#0d1b2a'], [0.25, '#1e3a5f'], [0.5, '#2b6cb0'], [0.75, '#4299e1'], [1, '#90cdf4']],
        zmin=0.5,
        zmax=1.0,
        text=[[f"{v:.3f}" for v in row] for row in segment_corr.values],
        texttemplate='%{text}',
        textfont=dict(size=14, color='white'),
        hovertemplate='<b>%{y}</b> vs <b>%{x}</b><br>Correlation: %{z:.3f}<extra></extra>'
    ))
    
    fig_seg_corr.update_layout(
        title='Segment Sales Correlation<br><sup>How customer segments move together over time</sup>',
        height=400,
        xaxis_title='',
        yaxis_title=''
    )
    st.plotly_chart(fig_seg_corr, use_container_width=True)
    
    # Find strongest and weakest correlations
    segs = segment_corr.columns.tolist()
    corr_pairs = []
    for i in range(len(segs)):
        for j in range(i+1, len(segs)):
            corr_pairs.append((segs[i], segs[j], segment_corr.iloc[i, j]))
    
    corr_pairs.sort(key=lambda x: x[2], reverse=True)
    strongest = corr_pairs[0] if corr_pairs else None
    weakest = corr_pairs[-1] if corr_pairs else None
    
    # Insight cards
    col_a, col_b = st.columns(2)
    with col_a:
        if strongest:
            st.markdown(f"""
            <div class="insight-card good" style="margin-top: 10px;">
                <div class="insight-icon">📈</div>
                <div class="insight-label">Strongest Correlation</div>
                <div class="insight-value">{strongest[0]} & {strongest[1]}</div>
                <div class="insight-detail">r = <strong>{strongest[2]:.3f}</strong> — These segments move together. Campaigns that boost one will likely lift the other.</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col_b:
        if weakest:
            st.markdown(f"""
            <div class="insight-card warn" style="margin-top: 10px;">
                <div class="insight-icon">📉</div>
                <div class="insight-label">Weakest Correlation</div>
                <div class="insight-value">{weakest[0]} & {weakest[1]}</div>
                <div class="insight-detail">r = <strong>{weakest[2]:.3f}</strong> — These segments behave independently. Tailored strategies recommended.</div>
            </div>
            """, unsafe_allow_html=True)

    # ADDITIONAL INSIGHT: Category Performance Analysis
    st.markdown("### 📊 Category Performance Insights")
    
    # Calculate category metrics
    cat_metrics = filtered_df.groupby('Category').agg({
        'Sales': ['sum', 'mean'],
        'Order ID': 'nunique',
        'Sub-Category': 'nunique'
    }).round(2)
    
    cat_metrics.columns = ['Total Sales', 'Avg Sale', 'Unique Orders', 'Unique Sub-Categories']
    cat_metrics = cat_metrics.reset_index()
    cat_metrics['Total Sales'] = cat_metrics['Total Sales'].apply(lambda x: f"${x:,.0f}")
    cat_metrics['Avg Sale'] = cat_metrics['Avg Sale'].apply(lambda x: f"${x:,.2f}")
    
    # Display category metrics in a clean format
    for _, row in cat_metrics.iterrows():
        category = row['Category']
        total_sales = row['Total Sales']
        avg_sale = row['Avg Sale']
        orders = f"{row['Unique Orders']:,}"
        subcats = int(row['Unique Sub-Categories'])
        
        # Color coding based on category
        if category == 'Technology':
            icon = "💻"
            color = "#4299e1"
        elif category == 'Furniture':
            icon = "🪑"
            color = "#48bb78"
        else:  # Office Supplies
            icon = "📎"
            color = "#ed8936"
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #0d1b2a 0%, #1b2a3b 100%);
                    border-left: 4px solid {color};
                    border-radius: 8px;
                    padding: 15px;
                    margin-bottom: 10px;">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                <span style="font-size: 1.5rem;">{icon}</span>
                <span style="font-size: 1.2rem; font-weight: 600; color: white;">{category}</span>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                <div>
                    <div style="font-size: 0.7rem; color: #a0aec0;">TOTAL SALES</div>
                    <div style="font-size: 1.1rem; font-weight: 600; color: white;">{total_sales}</div>
                </div>
                <div>
                    <div style="font-size: 0.7rem; color: #a0aec0;">AVG SALE</div>
                    <div style="font-size: 1.1rem; font-weight: 600; color: white;">{avg_sale}</div>
                </div>
                <div>
                    <div style="font-size: 0.7rem; color: #a0aec0;">ORDERS</div>
                    <div style="font-size: 1.1rem; font-weight: 600; color: white;">{orders}</div>
                </div>
                <div>
                    <div style="font-size: 0.7rem; color: #a0aec0;">SUB-CATEGORIES</div>
                    <div style="font-size: 1.1rem; font-weight: 600; color: white;">{subcats}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Find top and bottom performing sub-categories
    top_subcat = subcat_sales.iloc[0]['Sub-Category']
    top_subcat_sales = subcat_sales.iloc[0]['Sales']
    bottom_subcat = subcat_sales.iloc[-1]['Sub-Category']
    bottom_subcat_sales = subcat_sales.iloc[-1]['Sales']
    
    st.markdown(f"""
    <div class="insight-card" style="margin-top: 10px;">
        <div class="insight-icon">💡</div>
        <div class="insight-label">Key Product Insight</div>
        <div class="insight-value">{top_subcat}</div>
        <div class="insight-detail">
            <strong>Top performer:</strong> ${top_subcat_sales:,.0f} in sales<br>
            <strong>Bottom performer:</strong> {bottom_subcat} (${bottom_subcat_sales:,.0f})<br>
            <strong>Opportunity:</strong> The top sub-category generates {(top_subcat_sales/bottom_subcat_sales):.1f}x more sales than the bottom. Consider reviewing pricing, marketing, or inventory for underperformers.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
