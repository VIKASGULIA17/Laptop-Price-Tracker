# 🛍️ Laptop Scout - Enhanced Streamlit Price Tracker

## 📋 Project Overview
This is a comprehensive laptop price tracking application built with Streamlit, featuring:

- **Beautiful Dashboard** with key metrics and top deals
- **Advanced Filtering** with search, brand, price, and rating filters  
- **Interactive Analytics** with plotly charts and insights
- **Laptop Comparison** tool for side-by-side analysis
- **Professional Design** with light theme and responsive cards

## 🎯 Features Implemented

### ✅ Dashboard Page
- **Top Deals Section**: Highlighted best buy now deals in attractive green cards
- **Key Metrics**: Total laptops, buy now deals, stable prices, high-rated laptops
- **Advanced Filters**: Price range, rating, brand selection, and search functionality
- **Export Functionality**: Download filtered results as CSV
- **Real-time Statistics**: Dynamic counts based on applied filters

### ✅ Laptop Details Page  
- **Card Layout**: Beautiful 2-column card display with hover effects
- **Enhanced Filtering**: Rating, price, stability, brand, and search filters
- **Sorting Options**: Sort by rating, price (both directions), or review count
- **Performance Insights**: Show best deals, highest rated, and price ranges
- **Visual Indicators**: Special styling for hot deals with green borders

### ✅ Price Insights & Analytics
- **Market Overview**: Key metrics cards with average/median price, deal rates
- **Interactive Charts**: Price distribution, rating distribution, scatter plots
- **Brand Analysis**: Average prices by brand and market share pie charts
- **Advanced Analytics**: RAM vs price correlation, rating vs reviews analysis
- **Market Intelligence**: Automated insights and smart shopping tips

### ✅ Compare Laptops
- **Side-by-side Comparison**: Select any two laptops for detailed comparison
- **Detailed Cards**: Complete specifications in beautiful gradient cards
- **Quick Metrics**: Price difference, rating difference, review count comparison
- **Smart Recommendations**: Visual indicators for better choices

## 🎨 Design Features

### Professional Light Theme
- Clean, modern interface with subtle gradients
- Consistent color scheme: Blues for primary, greens for deals, reds for warnings
- Card-based layouts with hover effects and smooth transitions
- Professional typography and spacing

### Interactive Elements  
- Smooth hover animations on laptop cards
- Color-coded tags for buy now status and price stability
- Responsive design that works on different screen sizes
- Clear visual hierarchy with proper use of whitespace

### Data Visualization
- Interactive Plotly charts with clean backgrounds
- Consistent color schemes across all visualizations
- Hover tooltips for additional information
- Professional chart styling with proper labels

## 📊 Database Structure

The app uses SQLite database with the following key columns:
- `title`: Laptop name and specifications
- `extracted_price`: Current price in USD
- `rating`: Customer rating (1-5 stars)
- `reviews`: Number of customer reviews
- `buy_now`: Deal status (Yes/No) 
- `stability_label`: Price stability (Stable/Unstable)
- `brand`: Extracted brand name (Apple, Lenovo, Dell, HP, etc.)
- `display_size`, `ram`, `disk_size`, `operating_system`: Technical specs
- `thumbnail`: Product image URL
- `link_clean`: Amazon product URL

## 🚀 Technical Implementation

### Libraries Used
- **Streamlit**: Main web framework
- **Pandas**: Data manipulation and analysis  
- **SQLite3**: Database connectivity
- **Plotly**: Interactive visualizations
- **NumPy**: Numerical computations

### Architecture
- **Single Page Application**: All functionality in one main.py file
- **Cached Data Loading**: @st.cache_data for performance
- **Modular Design**: Each page as separate conditional block
- **Responsive Layout**: Column-based layouts that adapt to screen size

## 📈 Performance Features

### Smart Filtering
- Real-time filter application with instant results
- Combine multiple filters (price, rating, brand, search)
- Maintains filter state across interactions
- Shows filtered result counts and statistics

### Export Capabilities  
- CSV export with current timestamp
- Downloads filtered data with all relevant columns
- Maintains data formatting and structure

## 💡 Innovative Features

### Market Intelligence
- Automated calculation of deal percentages
- Brand comparison and market positioning
- Value recommendations based on price/performance
- Smart shopping tips with data-driven insights

### Visual Enhancement
- Special styling for hot deals with green borders
- Gradient backgrounds for different card types  
- Emoji icons for better visual categorization
- Professional color coding for status indicators

## 🎯 Usage Instructions

1. **Dashboard**: Start here for overview and filtering
2. **Laptop Details**: Browse individual laptop cards with detailed filtering
3. **Price Insights**: Explore market trends and analytics
4. **Compare Laptops**: Select and compare any two laptops side-by-side

## 📱 Mobile Responsive
The app is designed to work well on different screen sizes with:
- Flexible column layouts
- Responsive card sizing
- Scalable text and images
- Touch-friendly interface elements

---

*Built with ❤️ using Streamlit | Professional laptop price tracking made simple*