import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="PolySportsLab Market Analysis",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
DB_FILE = "market_history.db"

# Database Connection
@st.experimental_memo(ttl=60)
def load_data():
    conn = sqlite3.connect(DB_FILE)
    query = "SELECT * FROM market_history"
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

# Main Dashboard
def main():
    st.title("🏀 PolySportsLab Market Analysis Dashboard")
    st.markdown("Monitor historical market data, whale activity, and smart money trends.")

    # Load Data
    try:
        df = load_data()
    except Exception as e:
        st.error(f"Error loading database: {e}")
        st.info("Please run `fetch_whale_analysis.py` to generate data first.")
        return

    if df.empty:
        st.warning("Database is empty. Run the fetch script to collect data.")
        return

    # Sidebar Filters
    st.sidebar.header("Filters")
    
    # Date Filter
    min_date = df['timestamp'].min().date()
    max_date = df['timestamp'].max().date()
    
    selected_date = st.sidebar.date_input(
        "Select Date",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    # Market Filter
    markets = df['market_title'].unique()
    selected_markets = st.sidebar.multiselect(
        "Select Markets",
        options=markets,
        default=markets[:1] if len(markets) > 0 else []
    )

    # Filter Data
    if isinstance(selected_date, tuple) and len(selected_date) == 2:
        start_date, end_date = selected_date
        mask_date = (df['timestamp'].dt.date >= start_date) & (df['timestamp'].dt.date <= end_date)
        df_filtered = df[mask_date]
    else:
        df_filtered = df

    if selected_markets:
        df_filtered = df_filtered[df_filtered['market_title'].isin(selected_markets)]

    # --- Overview Section ---
    st.header("Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Records", len(df_filtered))
    with col2:
        latest_ts = df['timestamp'].max()
        st.metric("Last Update", latest_ts.strftime("%Y-%m-%d %H:%M"))
    with col3:
        avg_whale = df_filtered['whale_concentration'].mean()
        st.metric("Avg Whale Concentration", f"{avg_whale:.2f}%")
    with col4:
        total_vol = df_filtered.groupby('market_title')['volume'].last().sum()
        st.metric("Total Volume (Latest)", f"${total_vol:,.0f}")

    # --- Trend Analysis ---
    st.header("📈 Market Trends")
    
    if not selected_markets:
        st.info("Please select at least one market in the sidebar to view trends.")
    else:
        tab1, tab2, tab3 = st.tabs(["Volume & Liquidity", "Whale Concentration", "Prices"])
        
        with tab1:
            fig_vol = px.line(df_filtered, x='timestamp', y='volume', color='market_title', 
                             title="Volume Over Time", markers=True)
            st.plotly_chart(fig_vol, use_container_width=True)
            
            fig_liq = px.line(df_filtered, x='timestamp', y='liquidity', color='market_title', 
                             title="Liquidity Over Time", markers=True)
            st.plotly_chart(fig_liq, use_container_width=True)
            
        with tab2:
            fig_whale = px.line(df_filtered, x='timestamp', y='whale_concentration', color='market_title',
                               title="Whale Concentration Trend", markers=True)
            st.plotly_chart(fig_whale, use_container_width=True)
            
        with tab3:
            # For prices, it's better to show one market at a time or separate charts
            for market in selected_markets:
                market_df = df_filtered[df_filtered['market_title'] == market]
                fig_price = go.Figure()
                fig_price.add_trace(go.Scatter(x=market_df['timestamp'], y=market_df['price_yes'], name='YES Price', line=dict(color='green')))
                fig_price.add_trace(go.Scatter(x=market_df['timestamp'], y=market_df['price_no'], name='NO Price', line=dict(color='red')))
                fig_price.update_layout(title=f"Price History: {market}", xaxis_title="Time", yaxis_title="Price")
                st.plotly_chart(fig_price, use_container_width=True)

    # --- Raw Data ---
    st.header("📄 Raw Data Explorer")
    with st.expander("View Raw Data"):
        st.dataframe(df_filtered.sort_values(by='timestamp', ascending=False))

    # --- Refresh Button ---
    if st.button('Refresh Data'):
        st.experimental_rerun()

if __name__ == "__main__":
    main()
