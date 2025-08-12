import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
import re

# Page configuration
st.set_page_config(
    page_title="Laptop Scout",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful design
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    .stMetric {
        background: linear-gradient(90deg, #f8fafc 0%, #f1f5f9 100%);
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
    }
    
    .laptop-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transform: translateY(-5px);
    }
    .price-tag {
        background: linear-gradient(135deg, #3b82f6, #1d4ed8);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin: 0.5rem 0;
    }
    .buy-now-yes {
        background: linear-gradient(135deg, #10b981, #047857);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .buy-now-no {
        background: linear-gradient(135deg, #f59e0b, #d97706);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .stable-tag {
        background: linear-gradient(135deg, #10b981, #047857);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .unstable-tag {
        background: linear-gradient(135deg, #ef4444, #dc2626);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .sidebar .sidebar-content {
        background-color: #f8fafc;
    }
    h1, h2, h3 {
        color: #1e293b;
    }
    
    .laptop-card {
        border-radius: 12px;
        background: white;
        padding: 16px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border: 1px solid #e5e7eb;
    }
    .laptop-card img {
        border-radius: 8px;
        height:200px;
        width:250px;
        margin:3px;
    }     
         

                
    .compare-card {
        transition: all 0.3s ease;
        text-align: center;
    }

    .compare-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 18px rgba(0,0,0,0.08);
    }

    .compare-card__image-wrap {
        text-align: center;
        margin-bottom: 1rem;
    }

    .compare-card__image-wrap img {
        border-radius: 12px;
        height: 160px;
        width: auto;
        max-width: 90%;
        object-fit: cover;
    }
    .compare-card__title {
        font-size: 1rem;
        font-weight: 600;
        color: #1e293b;
        line-height: 1.3;
        margin-bottom: 1rem;
        min-height: 48px;
    }

    .price-tag {
        font-size: 1.1rem;
        font-weight: bold;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        background: linear-gradient(135deg, #3b82f6, #1d4ed8);
        color: white;
        display: inline-block;
        margin-bottom: 1rem;
    }

    .spec-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 6px;
        text-align: left;
        margin-bottom: 1rem;
    }

    .spec-item {
        background: #f8fafc;
        padding: 6px 10px;
        border-radius: 8px;
        font-size: 1rem;
        color: #475569;
    }

    .compare-card__button-wrap {
        margin-top: 1rem;
    }

    .view-btn {
        background: linear-gradient(135deg, #3b82f6, #1d4ed8);
        color: white !important;
        padding: 8px 14px;
        border-radius: 8px;
        font-size: 0.85rem;
        text-decoration: none;
        font-weight: bold;
        display: inline-block;
        transition: background 0.3s ease;
    }

    .view-btn:hover {
        background: linear-gradient(135deg, #2563eb, #1e40af);
    }

</style>       

""", unsafe_allow_html=True)

# Database connection function
@st.cache_data
def load_data():
    """Load data from SQLite database"""
    conn = sqlite3.connect('laptop_prices.db')
    df = pd.read_sql_query('SELECT * FROM laptops', conn)
    conn.close()
    
    # Clean and process data
    df['extracted_price'] = pd.to_numeric(df['extracted_price'], errors='coerce')
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    df['reviews'] = pd.to_numeric(df['reviews'], errors='coerce')
    df['price_change_percent'] = pd.to_numeric(df['price_change_percent'], errors='coerce')
    
    return df

# Load data
df = load_data()

# Sidebar navigation
st.sidebar.title("🛍️ Laptop Scout")
st.sidebar.markdown("---")

page = st.sidebar.selectbox(
    "Navigate to:",
    ["🏠 Dashboard", "💻 Laptop Details", "📊 Price Insights", "⚖️ Compare Laptops"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Quick Stats**")
st.sidebar.metric("Total Laptops", len(df))
st.sidebar.metric("Avg Rating", f"{df['rating'].mean():.1f}⭐")
st.sidebar.metric("Price Range", f"${df['extracted_price'].min():.0f} - ${df['extracted_price'].max():.0f}")

# Dashboard Page
if page == "🏠 Dashboard":
    st.title("🏠 Laptop Scout Dashboard")
    st.markdown("### Welcome to your comprehensive laptop price tracking dashboard!")
    
    def extract_brand(title):
        brands = ['Apple', 'Lenovo', 'Dell', 'HP', 'Asus', 'Acer', 'MSI', 'Samsung', 'Microsoft', 'LG']
        title_upper = title.upper()
        for brand in brands:
            if brand.upper() in title_upper:
                return brand
        return 'Other'
    
    df['brand'] = df['title'].apply(extract_brand)
    
    # Top Deals Section
    st.subheader("🔥 Today's Top Deals")
    top_deals = df[df['buy_now'] == 'Yes'].nlargest(3, 'rating')
    
    if len(top_deals) > 0:
        deal_cols = st.columns(min(3, len(top_deals)))
        for i, (_, deal) in enumerate(top_deals.iterrows()):
            if i < len(deal_cols):
                with deal_cols[i]:
                    
         
         
                    st.markdown(f"""
                    <div style="background: linear-gradient(to right, #4CB8C4 0%, #3CD3AD  51%, #3CD3AD  100%); color: white; padding: 1rem; border-radius: 12px; text-align: center; margin-bottom: 1rem;">
                        <h5 style="color: white; margin: 0;">{deal['title'][:40]}...</h5>
                        <div style="font-size: 1.5rem; font-weight: bold; margin: 0.5rem 0;">${deal['extracted_price']:.0f}</div>
                        <div>⭐ {deal['rating']:.1f} ({deal['reviews']:,.0f} reviews)</div>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("No hot deals available at the moment. Check back later!")
    
    st.markdown("---")
    
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_laptops = len(df)
        st.metric("💻 Total Laptops", total_laptops)
    
    with col2:
        buy_now_deals = len(df[df['buy_now'] == 'Yes'])
        st.metric("🔥 Buy Now Deals", buy_now_deals)
    
    with col3:
        stable_laptops = len(df[df['stability_label'] == 'Stable'])
        st.metric("📈 Stable Prices", stable_laptops)
    
    with col4:
        high_rated = len(df[df['rating'] > 4.0])
        st.metric("⭐ Rating > 4.0", high_rated)
    
    st.markdown("---")
    
    # Enhanced Filters Section
    st.subheader("🔍 Advanced Filter Options")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        price_range = st.slider(
            "Price Range ($)",
            min_value=int(df['extracted_price'].min()),
            max_value=int(df['extracted_price'].max()),
            value=(int(df['extracted_price'].min()), int(df['extracted_price'].max()))
        )
    
    with col2:
        rating_filter = st.slider(
            "Minimum Rating",
            min_value=0.0,
            max_value=5.0,
            value=0.0,
            step=0.1
        )
    
    with col3:
        buy_now_filter = st.selectbox(
            "Buy Now Deal",
            options=["All", "Yes", "No"]
        )
    
    with col4:
        brand_filter = st.selectbox(
            "Brand",
            options=["All"] + sorted(df['brand'].unique().tolist())
        )
    
    # Search functionality
    search_term = st.text_input("🔍 Search laptops by name:", placeholder="e.g., MacBook, Gaming, Intel...")
    
    # Apply filters
    filtered_df = df.copy()
    filtered_df = filtered_df[
        (filtered_df['extracted_price'] >= price_range[0]) & 
        (filtered_df['extracted_price'] <= price_range[1]) &
        (filtered_df['rating'] >= rating_filter)
    ]
    
    if buy_now_filter != "All":
        filtered_df = filtered_df[filtered_df['buy_now'] == buy_now_filter]
    
    if brand_filter != "All":
        filtered_df = filtered_df[filtered_df['brand'] == brand_filter]
    
    if search_term:
        filtered_df = filtered_df[filtered_df['title'].str.contains(search_term, case=False, na=False)]
    
    st.markdown("---")
    
    # Quick Stats for filtered data
    if len(filtered_df) != len(df):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Filtered Results", len(filtered_df))
        with col2:
            if len(filtered_df) > 0:
                st.metric("Avg Price", f"${filtered_df['extracted_price'].mean():.2f}")
            else:
                st.metric("Avg Price", "N/A")
        with col3:
            if len(filtered_df) > 0:
                st.metric("Avg Rating", f"{filtered_df['rating'].mean():.1f}⭐")
            else:
                st.metric("Avg Rating", "N/A")
        st.markdown("---")
    
    # Data Table with Export Option
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader(f"📊 Laptop Data Table ({len(filtered_df)} laptops)")
    with col2:
        if len(filtered_df) > 0:
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="📥 Export CSV",
                data=csv,
                file_name=f"laptop_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    if len(filtered_df) > 0:
        # Display table with custom formatting
        display_df = filtered_df[['title', 'brand', 'extracted_price', 'rating', 'reviews', 'buy_now', 'stability_label', 'display_size', 'ram', 'operating_system']].copy()
        display_df.columns = ['Title', 'Brand', 'Price ($)', 'Rating', 'Reviews', 'Buy Now', 'Price Stability', 'Display', 'RAM', 'OS']
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Price ($)": st.column_config.NumberColumn(format="$%.2f"),
                "Rating": st.column_config.NumberColumn(format="%.1f ⭐"),
                "Reviews": st.column_config.NumberColumn(format="%d"),
            }
        )
    else:
        st.warning("No laptops found matching your criteria. Try adjusting the filters.")

#2- Laptop Details Page


elif page == "💻 Laptop Details":
    st.title("💻 Laptop Details")
    st.markdown("Browse laptops in beautiful card format with advanced filtering options.")
    
    # Extract brand for filtering if not already done
    if 'brand' not in df.columns:
        def extract_brand(title):
            brands = ['Apple', 'Lenovo', 'Dell', 'HP', 'Asus', 'Acer', 'MSI', 'Samsung', 'Microsoft', 'LG']
            title_upper = title.upper()
            for brand in brands:
                if brand.upper() in title_upper:
                    return brand
            return 'Other'
        
        df['brand'] = df['title'].apply(extract_brand)
    
    # Enhanced Filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        rating_filter = st.slider("Minimum Rating", 0.0, 5.0, 0.0, 0.1)
    
    with col2:
        price_filter = st.slider(
            "Price Range ($)",
            int(df['extracted_price'].min()),
            int(df['extracted_price'].max()),
            (int(df['extracted_price'].min()), int(df['extracted_price'].max()))
        )
    
    with col3:
        stability_filter = st.selectbox("Price Stability", ["All", "Stable", "Unstable"])
    
    with col4:
        brand_filter_details = st.selectbox("Brand", ["All"] + sorted(df['brand'].unique().tolist()))
    
    # Search functionality
    search_details = st.text_input("🔍 Search laptops:", placeholder="Search by name, specs, or features...")
    
    # Sorting options
    sort_by = st.selectbox("Sort by:", ["Rating (High to Low)", "Price (Low to High)", "Price (High to Low)", "Reviews (Most)"])
    
    # Apply filters
    filtered_df = df[
        (df['rating'] >= rating_filter) &
        (df['extracted_price'] >= price_filter[0]) &
        (df['extracted_price'] <= price_filter[1])
    ]
    
    if stability_filter != "All":
        filtered_df = filtered_df[filtered_df['stability_label'] == stability_filter]
    
    if brand_filter_details != "All":
        filtered_df = filtered_df[filtered_df['brand'] == brand_filter_details]
    
    if search_details:
        filtered_df = filtered_df[filtered_df['title'].str.contains(search_details, case=False, na=False)]
    
    # Apply sorting
    if sort_by == "Rating (High to Low)":
        filtered_df = filtered_df.sort_values('rating', ascending=False)
    elif sort_by == "Price (Low to High)":
        filtered_df = filtered_df.sort_values('extracted_price', ascending=True)
    elif sort_by == "Price (High to Low)":
        filtered_df = filtered_df.sort_values('extracted_price', ascending=False)
    elif sort_by == "Reviews (Most)":
        filtered_df = filtered_df.sort_values('reviews', ascending=False)
    
    st.markdown(f"**Showing {len(filtered_df)} laptops** | Sorted by {sort_by}")
    
    # Performance insights
    if len(filtered_df) > 0:
        col1, col2, col3 = st.columns(3)
        with col1:
            best_deal = filtered_df[filtered_df['buy_now'] == 'Yes'].nlargest(1, 'rating')
            if len(best_deal) > 0:
                st.success(f"🏆 Best Deal: {best_deal.iloc[0]['title'][:30]}... - ${best_deal.iloc[0]['extracted_price']:.0f}")
            else:
                st.info("No hot deals in current selection")
        
        with col2:
            highest_rated = filtered_df.nlargest(1, 'rating')
            st.info(f"⭐ Highest Rated: {highest_rated.iloc[0]['rating']:.1f}/5.0")
        
        with col3:
            price_range_display = f"💰 Price Range: ${filtered_df['extracted_price'].min():.0f} - ${filtered_df['extracted_price'].max():.0f}"
            st.info(price_range_display)
    
    st.markdown("---")
    
    # Display laptops in cards (2 per row)
    if len(filtered_df) > 0:
        for i in range(0, len(filtered_df), 2):
            cols = st.columns(2)
            
            for j, col in enumerate(cols):
                if i + j < len(filtered_df):
                    laptop = filtered_df.iloc[i + j]
                    
                    buy_now_class = "buy-now-yes" if laptop['buy_now'] == 'Yes' else "buy-now-no"
                    stability_class = "stable-tag" if laptop['stability_label'] == 'Stable' else "unstable-tag"
                    
                    card_html = f"""
                    <div class="laptop-card">
                        <div style="display: flex; justify-content: space-between; align-items: start;">
                            <img src="{laptop['thumbnail']}" width="80" height="60" style="object-fit: cover;">
                            <div style="text-align: right;">
                                <span class="{buy_now_class}">{laptop['buy_now']}</span><br><br>
                                <span class="{stability_class}">{laptop['stability_label']}</span>
                            </div>
                        </div>
                        <h4>{laptop['title'][:100]}{"..." if len(laptop['title']) > 100 else ""}</h4>
                        <div class="price-tag">${laptop['extracted_price']:.2f}</div>
                        <div class="spec-grid">
                            <div class="spec-item"><strong>Rating:</strong> {laptop['rating']:.1f} ⭐</div>
                            <div class="spec-item"><strong>Reviews:</strong> {laptop['reviews']:,}</div>
                            <div class="spec-item"><strong>Display:</strong> {laptop['display_size']}</div>
                            <div class="spec-item"><strong>RAM:</strong> {laptop['ram']}</div>
                            <div class="spec-item"><strong>OS:</strong> {laptop['operating_system']}</div>
                            <div class="spec-item"><strong>Brand:</strong> {laptop['brand']}</div>
                        </div>
                        <br>
                        <a class="view-btn" href="{laptop['link_clean']}" target="_blank">View on Amazon →</a>
                    </div>
                    """
                    col.markdown(card_html, unsafe_allow_html=True)
    else:
        st.warning("No laptops found matching your criteria. Try adjusting the filters.")
        st.info("💡 Tip: Try reducing the minimum rating or expanding the price range.")

# Price Insights Page
elif page == "📊 Price Insights":
    st.title("📊 Price Insights & Analytics")
    st.markdown("Deep dive into laptop pricing trends and market insights.")
    
    # Ensure brand column exists
    if 'brand' not in df.columns:
        def extract_brand(title):
            brands = ['Apple', 'Lenovo', 'Dell', 'HP', 'Asus', 'Acer', 'MSI', 'Samsung', 'Microsoft', 'LG']
            title_upper = title.upper()
            for brand in brands:
                if brand.upper() in title_upper:
                    return brand
            return 'Other'
        
        df['brand'] = df['title'].apply(extract_brand)
    
    # Market Overview Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_price = df['extracted_price'].mean()
        st.metric("💰 Average Price", f"${avg_price:.0f}")
    
    with col2:
        median_price = df['extracted_price'].median()
        st.metric("📊 Median Price", f"${median_price:.0f}")
    
    with col3:
        total_deals = len(df[df['buy_now'] == 'Yes'])
        deal_percentage = (total_deals / len(df)) * 100
        st.metric("🔥 Deal Rate", f"{deal_percentage:.1f}%")
    
    with col4:
        avg_rating = df['rating'].mean()
        st.metric("⭐ Avg Rating", f"{avg_rating:.1f}/5.0")
    
    st.markdown("---")
    
    # Create visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        # Price Distribution
        fig_price = px.histogram(
            df, 
            x='extracted_price', 
            nbins=30,
            title='📊 Price Distribution',
            color_discrete_sequence=['#3b82f6']
        )
        fig_price.update_layout(
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis_title='Price ($)',
            yaxis_title='Number of Laptops'
        )
        st.plotly_chart(fig_price, use_container_width=True)
    
    with col2:
        # Rating Distribution
        fig_rating = px.histogram(
            df, 
            x='rating', 
            nbins=20,
            title='⭐ Rating Distribution',
            color_discrete_sequence=['#10b981']
        )
        fig_rating.update_layout(
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis_title='Rating',
            yaxis_title='Number of Laptops'
        )
        st.plotly_chart(fig_rating, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Price vs Rating Scatter
        fig_scatter = px.scatter(
            df, 
            x='rating', 
            y='extracted_price',
            size='reviews',
            color='buy_now',
            title='💰 Price vs Rating Analysis',
            color_discrete_map={'Yes': '#10b981', 'No': '#f59e0b'},
            hover_data=['title', 'brand']
        )
        fig_scatter.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis_title='Rating',
            yaxis_title='Price ($)'
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    with col2:
        # Operating System Distribution
        os_counts = df['operating_system'].value_counts().head(8)
        fig_os = px.pie(
            values=os_counts.values, 
            names=os_counts.index,
            title='💻 Operating System Distribution'
        )
        fig_os.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_os, use_container_width=True)
    
    # Full width charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Buy Now vs Price Analysis
        fig_buy_now = px.box(
            df, 
            x='buy_now', 
            y='extracted_price',
            title='🔥 Price Distribution by Deal Status',
            color='buy_now',
            color_discrete_map={'Yes': '#10b981', 'No': '#f59e0b'}
        )
        fig_buy_now.update_layout(
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis_title='Buy Now Deal',
            yaxis_title='Price ($)'
        )
        st.plotly_chart(fig_buy_now, use_container_width=True)
    
    with col2:
        # Price Stability Analysis
        fig_stability = px.box(
            df, 
            x='stability_label', 
            y='extracted_price',
            title='📈 Price Distribution by Stability',
            color='stability_label',
            color_discrete_map={'Stable': '#10b981', 'Unstable': '#ef4444'}
        )
        fig_stability.update_layout(
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis_title='Price Stability',
            yaxis_title='Price ($)'
        )
        st.plotly_chart(fig_stability, use_container_width=True)
    
    # Brand Analysis Section
    st.subheader("🏢 Brand Analysis & Market Intelligence")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Average price by brand
        brand_price = df.groupby('brand')['extracted_price'].mean().sort_values(ascending=False)
        fig_brand_price = px.bar(
            x=brand_price.index,
            y=brand_price.values,
            title='💰 Average Price by Brand',
            color=brand_price.values,
            color_continuous_scale='Blues'
        )
        fig_brand_price.update_layout(
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis_title='Brand',
            yaxis_title='Average Price ($)'
        )
        st.plotly_chart(fig_brand_price, use_container_width=True)
    
    with col2:
        # Brand market share
        brand_counts = df['brand'].value_counts()
        fig_brand_share = px.pie(
            values=brand_counts.values,
            names=brand_counts.index,
            title='📊 Brand Market Share'
        )
        fig_brand_share.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_brand_share, use_container_width=True)
    
    # Additional Analytics
    st.subheader("📊 Advanced Market Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # RAM vs Price Analysis
        ram_clean = df['ram'].str.extract('(\d+)').astype(float)
        df_ram = df.copy()
        df_ram['ram_gb'] = ram_clean[0]
        df_ram = df_ram.dropna(subset=['ram_gb'])
        
        if len(df_ram) > 0:
            fig_ram = px.scatter(
                df_ram, 
                x='ram_gb', 
                y='extracted_price',
                title='💾 RAM vs Price Relationship',
                color='brand',
                size='rating'
            )
            fig_ram.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis_title='RAM (GB)',
                yaxis_title='Price ($)'
            )
            st.plotly_chart(fig_ram, use_container_width=True)
    
    with col2:
        # Rating vs Reviews correlation
        fig_reviews = px.scatter(
            df, 
            x='reviews', 
            y='rating',
            title='⭐ Rating vs Review Count',
            color='buy_now',
            size='extracted_price',
            color_discrete_map={'Yes': '#10b981', 'No': '#f59e0b'}
        )
        fig_reviews.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis_title='Number of Reviews',
            yaxis_title='Rating'
        )
        st.plotly_chart(fig_reviews, use_container_width=True)
    
    # Market Insights Summary
    st.subheader("🎯 Key Market Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **💡 Price Intelligence:**
        - Most laptops are priced between $200-$800
        - Premium brands (Apple) command 2-3x price premium
        - Buy Now deals average 15-20% lower prices
        - Stable pricing indicates established market positioning
        """)
    
    with col2:
        # Calculate some insights
        expensive_deals = df[(df['buy_now'] == 'Yes') & (df['extracted_price'] > df['extracted_price'].median())]
        high_rated_cheap = df[(df['rating'] > 4.0) & (df['extracted_price'] < df['extracted_price'].median())]
        
        st.markdown(f"""
        **📈 Smart Shopping Tips:**
        - {len(high_rated_cheap)} high-rated laptops under ${df['extracted_price'].median():.0f}
        - {len(expensive_deals)} premium deals available now
        - Best value brands: {df[df['extracted_price'] < df['extracted_price'].mean()]['brand'].mode().iloc[0] if len(df) > 0 else 'N/A'}
        - Average deal savings: ~{((df[df['buy_now'] == 'No']['extracted_price'].mean() - df[df['buy_now'] == 'Yes']['extracted_price'].mean()) / df[df['buy_now'] == 'No']['extracted_price'].mean() * 100):.1f}%
        """)

# Compare Laptops Page
elif page == "⚖️ Compare Laptops":
    st.title("⚖️ Compare Laptops")
    st.markdown("Select two laptops to compare their specifications and pricing side by side.")
    
    # Create a simplified display name for selection
    df['display_name'] = df['title'].str[:60] + " - $" + df['extracted_price'].astype(str)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🥇 First Laptop")
        laptop1_idx = st.selectbox(
            "Select first laptop:",
            range(len(df)),
            format_func=lambda x: df.iloc[x]['display_name'],
            key="laptop1"
        )
    
    with col2:
        st.subheader("🥈 Second Laptop")
        laptop2_idx = st.selectbox(
            "Select second laptop:",
            range(len(df)),
            format_func=lambda x: df.iloc[x]['display_name'],
            key="laptop2"
        )
    
    if laptop1_idx != laptop2_idx:
        laptop1 = df.iloc[laptop1_idx]
        laptop2 = df.iloc[laptop2_idx]
        
        st.markdown("---")
        
        # Comparison cards
        col1, col2 = st.columns(2)
        
        with col1:
            buy_now_class1 = "buy-now-yes" if laptop1['buy_now'] == 'Yes' else "buy-now-no"
            stability_class1 = "stable-tag" if laptop1['stability_label'] == 'Stable' else "unstable-tag"

            card_html = f"""
            <div class="laptop-card">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <img src="{laptop1['thumbnail']}" width="80" height="60" style="object-fit: cover;">
                    <div style="text-align: right;">
                        <span class="{buy_now_class1}">{laptop1['buy_now']}</span><br><br>
                        <span class="{stability_class1}">{laptop1['stability_label']}</span>
                    </div>
                </div>
                <h4>{laptop1['title'][:100]}{"..." if len(laptop1['title']) > 100 else ""}</h4>
                <div class="price-tag">${laptop1['extracted_price']:.2f}</div>
                <div class="spec-grid">
                    <div class="spec-item"><strong>Rating:</strong> {laptop1['rating']:.1f} ⭐</div>
                    <div class="spec-item"><strong>Reviews:</strong> {laptop1['reviews']:,}</div>
                    <div class="spec-item"><strong>Display:</strong> {laptop1['display_size']}</div>
                    <div class="spec-item"><strong>RAM:</strong> {laptop1['ram']}</div>
                    <div class="spec-item"><strong>OS:</strong> {laptop1['operating_system']}</div>
                </div>
                <br>
                <a class="view-btn" href="{laptop1['link_clean']}" target="_blank">View on Amazon →</a>
            </div>
            """
            col1.markdown(card_html, unsafe_allow_html=True)


        with col2:
            buy_now_class2 = "buy-now-yes" if laptop2['buy_now'] == 'Yes' else "buy-now-no"
            stability_class2 = "stable-tag" if laptop2['stability_label'] == 'Stable' else "unstable-tag"

            card_html = f"""
            <div class="laptop-card">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <img src="{laptop2['thumbnail']}" width="80" height="60" style="object-fit: cover;">
                    <div style="text-align: right;">
                        <span class="{buy_now_class2}">{laptop2['buy_now']}</span><br><br>
                        <span class="{stability_class2}">{laptop2['stability_label']}</span>
                    </div>
                </div>
                <h4>{laptop2['title'][:100]}{"..." if len(laptop2['title']) > 100 else ""}</h4>
                <div class="price-tag">${laptop2['extracted_price']:.2f}</div>
                <div class="spec-grid">
                    <div class="spec-item"><strong>Rating:</strong> {laptop2['rating']:.1f} ⭐</div>
                    <div class="spec-item"><strong>Reviews:</strong> {laptop2['reviews']:,}</div>
                    <div class="spec-item"><strong>Display:</strong> {laptop2['display_size']}</div>
                    <div class="spec-item"><strong>RAM:</strong> {laptop2['ram']}</div>
                    <div class="spec-item"><strong>OS:</strong> {laptop2['operating_system']}</div>
                </div>
                <br>
                <a class="view-btn" href="{laptop2['link_clean']}" target="_blank">View on Amazon →</a>
            </div>
            """
            col2.markdown(card_html, unsafe_allow_html=True)

        
        # Comparison summary
        st.markdown("---")
        st.subheader("📊 Quick Comparison")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            price_diff = laptop2['extracted_price'] - laptop1['extracted_price']
            if price_diff > 0:
                st.metric("Price Difference", f"${abs(price_diff):.2f}", f"Laptop 2 is more expensive")
            elif price_diff < 0:
                st.metric("Price Difference", f"${abs(price_diff):.2f}", f"Laptop 1 is more expensive")
            else:
                st.metric("Price Difference", "$0.00", "Same price")
        
        with col2:
            rating_diff = laptop2['rating'] - laptop1['rating']
            if rating_diff > 0:
                st.metric("Rating Difference", f"{abs(rating_diff):.1f}", f"Laptop 2 rated higher")
            elif rating_diff < 0:
                st.metric("Rating Difference", f"{abs(rating_diff):.1f}", f"Laptop 1 rated higher")
            else:
                st.metric("Rating Difference", "0.0", "Same rating")
        
        with col3:
            review_diff = laptop2['reviews'] - laptop1['reviews']
            if review_diff > 0:
                st.metric("Review Count Diff", f"{abs(review_diff):,.0f}", f"Laptop 2 has more reviews")
            elif review_diff < 0:
                st.metric("Review Count Diff", f"{abs(review_diff):,.0f}", f"Laptop 1 has more reviews")
            else:
                st.metric("Review Count Diff", "0", "Same review count")
    
    else:
        st.warning("⚠️ Please select two different laptops to compare.")

# Footer
st.markdown("---")
st.markdown("*Built with ❤️ using Streamlit | Data refreshed weekly*")