import streamlit as st
import pandas as pd
import plotly.express as px
from windrose import WindroseAxes
import matplotlib.pyplot as plt

# Load Data
@st.cache_data
def load_data():
    # Replace with your actual cleaned dataset path
    return pd.read_csv("../data/cleaned_data.csv")

# Application Title
st.title("Solar Radiation Analysis Dashboard")
st.sidebar.header("Dashboard Navigation")

# Load Data
data = load_data()

# Sidebar Navigation
page = st.sidebar.selectbox(
    "Select a Visualization",
    ["Overview", "Time Series Analysis", "Correlation Analysis", "Wind Analysis", "Temperature Analysis"]
)

# Overview Page
if page == "Overview":
    st.subheader("Dataset Overview")
    st.dataframe(data.head())
    st.write("Summary Statistics:")
    st.write(data.describe())


elif page == "Time Series Analysis":
    st.subheader("Time Series Analysis")

    data['Timestamp'] = pd.to_datetime(data['Timestamp'])  # Convert to datetime
    data.set_index('Timestamp', inplace=True)  # Set as index for resampling
    
    # Metric selection
    metric = st.selectbox("Select a Metric", ["GHI", "DNI", "DHI", "Tamb"])
    
    # Aggregation level
    aggregation = st.radio("Aggregation Level", ["Daily", "Monthly"], index=0)
    if aggregation == "Daily":
        grouped = data[[metric]].resample('D').mean()
    elif aggregation == "Monthly":
        grouped = data[[metric]].resample('M').mean()
    
    # Plot the selected metric
    fig = px.line(
        grouped,
        x=grouped.index,
        y=metric,
        title=f"{aggregation} Average of {metric}",
        labels={"x": "Date", "y": metric},
        markers=True
    )
    st.plotly_chart(fig)
    
    # Reset index to maintain original data structure
    data.reset_index(inplace=True)

# Correlation Analysis
elif page == "Correlation Analysis":
    st.subheader("Correlation Matrix")
    
    # Ensure Timestamp is a datetime object
    data['Timestamp'] = pd.to_datetime(data['Timestamp'])  # Convert to datetime
    data.set_index('Timestamp', inplace=True)  # Set as index for resampling
    
    # Calculate correlation matrix
    corr_matrix = data.corr()
    
    # Create heatmap with larger dimensions
    fig = px.imshow(
        corr_matrix,
        title="Correlation Heatmap",
        labels=dict(color="Correlation"),
        width=800,  # Set desired width
        height=600  # Set desired height
    )
    
    # Display the plot
    st.plotly_chart(fig)


# Wind Analysis

elif page == "Wind Analysis":
    st.subheader("Wind Speed and Direction")
    
    # Ensure the required columns exist
    if 'WS' not in data.columns or 'WD' not in data.columns:
        st.error("Wind Speed (WS) or Wind Direction (WD) data is missing.")
    else:
        # Create a wind rose plot
        fig, ax = plt.subplots(figsize=(6,6))
        ax = WindroseAxes.from_ax(fig=fig)
        ax.bar(
            data['WD'],  # Wind Direction (degrees)
            data['WS'],  # Wind Speed (m/s)
            normed=True,
            opening=0.8,
            edgecolor='white'
        )
        ax.set_title("Wind Rose: Wind Speed and Direction")
        
        # Display the plot in Streamlit
        st.pyplot(fig)


# Temperature Analysis
elif page == "Temperature Analysis":
    st.subheader("Temperature and Humidity Impact")
    scatter_fig = px.scatter(
        data,
        x="Tamb",
        y="GHI",
        size="RH",
        color="RH",
        labels={"Tamb": "Ambient Temperature (°C)", "GHI": "Global Horizontal Irradiance (W/m²)"},
        title="Temperature vs. Solar Radiation (Bubble Size: RH)"
    )
    st.plotly_chart(scatter_fig)
