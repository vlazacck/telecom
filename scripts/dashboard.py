import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px



# Define PostgreSQL connection parameters
db_config = {
    'dbname': 'telecom',       # Replace with your database name
    'user': 'postgres',        # Replace with your username
    'password': 'your_password',  # Replace with your actual password
    'host': 'localhost',       # Replace with your host (default is localhost)
    'port': 5432               # Default PostgreSQL port
}

# Create a connection engine
try:
    engine = create_engine(
        f"postgresql+psycopg2://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['dbname']}"
    )
    print("PostgreSQL connection established successfully.")
except Exception as e:
    st.error(f"Failed to connect to the PostgreSQL database: {e}")
    st.stop()

# Function to load data from PostgreSQL
def load_data(table_name):
    """
    Load data from PostgreSQL database.

    Args:
        table_name (str): Name of the table to load.

    Returns:
        pd.DataFrame: Loaded data or None if an error occurs.
    """
    try:
        print(f"Loading data from table '{table_name}'...")
        data = pd.read_sql(f"SELECT * FROM {table_name}", con=engine)
        print(f"Data loaded successfully from table '{table_name}'.")
        return data
    except Exception as e:
        st.error(f"Error loading data from table '{table_name}': {e}")
        st.stop()

# Load datasets
user_behavior = load_data('user_behavior')  # From Task 1
if user_behavior is None:
    st.error("Failed to load user behavior data. Please check the database connection and table existence.")
    st.stop()

experience_metrics = load_data('experience_metrics_with_clusters')  # From Task 3
if experience_metrics is None:
    st.error("Failed to load experience metrics data. Please check the database connection and table existence.")
    st.stop()

customer_satisfaction = load_data('customer_satisfaction')  # From Task 4
if customer_satisfaction is None:
    st.error("Failed to load customer satisfaction data. Please check the database connection and table existence.")
    st.stop()

# Set page configuration
st.set_page_config(page_title="TellCo Analytics Dashboard", layout="wide")

# Sidebar navigation
page = st.sidebar.selectbox("Select Analysis Page", [
    "User Overview Analysis",
    "User Engagement Analysis",
    "Experience Analysis",
    "Satisfaction Analysis"
])

# Page content
if page == "User Overview Analysis":
    st.title("User Overview Analysis")
    
    # Check if required columns exist
    if 'Handset Type' not in user_behavior.columns:
        st.error("Missing 'Handset Type' column in user_behavior dataset.")
        st.stop()
    
    # Top handsets
    top_handsets = user_behavior['Handset Type'].value_counts().head(10)
    fig = px.bar(top_handsets, x=top_handsets.values, y=top_handsets.index, orientation='h', title="Top 10 Handsets by Usage")
    st.plotly_chart(fig)

    # Top manufacturers
    if 'Handset Manufacturer' not in user_behavior.columns:
        st.error("Missing 'Handset Manufacturer' column in user_behavior dataset.")
        st.stop()
    
    top_manufacturers = user_behavior['Handset Manufacturer'].value_counts().head(3)
    fig = px.pie(top_manufacturers, values=top_manufacturers.values, names=top_manufacturers.index, title="Top 3 Manufacturers by Market Share")
    st.plotly_chart(fig)

elif page == "User Engagement Analysis":
    st.title("User Engagement Analysis")

    # Check if required columns exist
    if 'Session Frequency' not in experience_metrics.columns:
        st.error("Missing 'Session Frequency' column in experience_metrics dataset.")
        st.stop()
    
    # Top 10 users by session frequency
    top_10_session_frequency = experience_metrics.sort_values(by='Session Frequency', ascending=False).head(10)
    fig = px.bar(top_10_session_frequency, x='MSISDN/Number', y='Session Frequency', title="Top 10 Users by Session Frequency")
    st.plotly_chart(fig)

    # K-Means clusters for engagement
    if 'Experience Cluster' not in experience_metrics.columns:
        st.error("Missing 'Experience Cluster' column in experience_metrics dataset.")
        st.stop()
    
    fig = px.scatter(
        experience_metrics,
        x='Total Session Duration (ms)',
        y='Total Data (Bytes)',
        color='Experience Cluster',
        title="K-Means Clustering of User Engagement"
    )
    st.plotly_chart(fig)

elif page == "Experience Analysis":
    st.title("Experience Analysis")

    # Check if required columns exist
    if 'Handset Type' not in experience_metrics.columns:
        st.error("Missing 'Handset Type' column in experience_metrics dataset.")
        st.stop()
    
    # Throughput per handset type
    throughput_per_handset = experience_metrics.groupby('Handset Type')['Avg Total Throughput (kbps)'].mean().sort_values(ascending=False).head(10)
    fig = px.bar(throughput_per_handset, x=throughput_per_handset.values, y=throughput_per_handset.index, orientation='h', title="Average Throughput per Handset Type")
    st.plotly_chart(fig)

    # TCP retransmission per handset type
    if 'Avg TCP Retransmission (DL)' not in experience_metrics.columns:
        st.error("Missing 'Avg TCP Retransmission (DL)' column in experience_metrics dataset.")
        st.stop()
    
    tcp_retransmission_per_handset = experience_metrics.groupby('Handset Type')['Avg TCP Retransmission (DL)'].mean().sort_values(ascending=False).head(10)
    fig = px.bar(tcp_retransmission_per_handset, x=tcp_retransmission_per_handset.values, y=tcp_retransmission_per_handset.index, orientation='h', title="Average TCP Retransmission per Handset Type")
    st.plotly_chart(fig)

elif page == "Satisfaction Analysis":
    st.title("Satisfaction Analysis")

    # Check if required columns exist
    if 'Satisfaction Score' not in customer_satisfaction.columns:
        st.error("Missing 'Satisfaction Score' column in customer_satisfaction dataset.")
        st.stop()
    
    # Top 10 satisfied customers
    top_10_satisfied = customer_satisfaction.sort_values(by='Satisfaction Score', ascending=False).head(10)
    fig = px.bar(top_10_satisfied, x='MSISDN/Number', y='Satisfaction Score', title="Top 10 Satisfied Customers")
    st.plotly_chart(fig)

    # Satisfaction clusters
    if 'Satisfaction Cluster' not in customer_satisfaction.columns:
        st.error("Missing 'Satisfaction Cluster' column in customer_satisfaction dataset.")
        st.stop()
    
    fig = px.scatter(
        customer_satisfaction,
        x='Engagement Score',
        y='Experience Score',
        color='Satisfaction Cluster',
        title="K-Means Clustering of Customer Satisfaction"
    )
    st.plotly_chart(fig)

    # Average satisfaction and experience score per cluster
    satisfaction_summary = customer_satisfaction.groupby('Satisfaction Cluster').agg({
        'Satisfaction Score': 'mean',
        'Experience Score': 'mean',
        'Engagement Score': 'mean'
    }).reset_index()

    fig = px.bar(
        satisfaction_summary,
        x='Satisfaction Cluster',
        y=['Satisfaction Score', 'Experience Score', 'Engagement Score'],
        barmode='group',
        title="Average Scores per Satisfaction Cluster"
    )
    st.plotly_chart(fig)