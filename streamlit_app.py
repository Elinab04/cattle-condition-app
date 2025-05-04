import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Page configuration
st.set_page_config(page_title='Cattle Health Conditions Dashboard', layout='wide')

@st.cache_data
def load_data(path):
    """Load and clean the cattle conditions dataset."""
    df = pd.read_csv(path)
    # Parse YearMonth to datetime
    df['YearMonth'] = pd.to_datetime(df['YearMonth'] + '-01')
    df['Condition'] = df['Condition'].str.strip()
    return df

# Load dataset from data folder
DATA_PATH = 'cattle-conditions-oct-20-dec-20.csv'

try:
    df = load_data(DATA_PATH)
except FileNotFoundError:
    st.error(f"Dataset not found at {DATA_PATH}. Please upload the CSV to the data/ folder.")
    st.stop()

# Sidebar filters
st.sidebar.header('Filters')
species = st.sidebar.multiselect('Select Species', df['Species'].unique(), df['Species'].unique())
inspection_types = st.sidebar.multiselect('Select Inspection Type', df['InspectionType'].unique(), df['InspectionType'].unique())
date_range = st.sidebar.date_input('Select Month Range', [df['YearMonth'].min().date(), df['YearMonth'].max().date()])

# Convert dates for filtering
start_date = pd.to_datetime(date_range[0])
end_date = pd.to_datetime(date_range[1])

# Apply filters
mask = (
    df['Species'].isin(species) &
    df['InspectionType'].isin(inspection_types) &
    (df['YearMonth'] >= start_date) &
    (df['YearMonth'] <= end_date)
)
filtered = df.loc[mask]

# Main dashboard title
st.title('Cattle Health Conditions Dashboard')

# Summary Metrics
col1, col2, col3 = st.columns(3)
col1.metric('Total Conditions', int(filtered['NumberOfConditions'].sum()))
col2.metric('Avg % of Throughput', f"{filtered['PercentageOfThroughput'].mean():.2f}%")
col3.metric('Reporting Plants', int(filtered['NumberOfThroughputPlants'].max()))

st.markdown('---')

# Insight 1: Temporal Trend of Conditions
monthly = filtered.groupby('YearMonth')['NumberOfConditions'].sum()
fig1, ax1 = plt.subplots()
ax1.plot(monthly.index, monthly.values)
ax1.set_title('Total Conditions Over Time')
st.pyplot(fig1)