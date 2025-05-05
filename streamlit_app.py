import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np 

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

if not species:
    species = df['Species'].unique()
if not inspection_types:
    inspection_types = df['InspectionType'].unique()


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
st.subheader('Conditions Over Time')
st.markdown('This line chart shows the total number of detected health conditions each month to highlight temporal trends and seasonal patterns.')
monthly = filtered.groupby('YearMonth')['NumberOfConditions'].sum()
fig1, ax1 = plt.subplots()
ax1.plot(monthly.index, monthly.values)
ax1.set_title('Total Conditions Over Time')
ax1.set_xlabel('Month')
ax1.set_ylabel('Number of Conditions')
# Show only month labels on x-axis
import matplotlib.dates as mdates
ax1.xaxis.set_major_locator(mdates.MonthLocator())
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
fig1.autofmt_xdate()
st.pyplot(fig1)

# Insight 2: Species-Specific Condition Rates 
st.subheader('Condition Rate by Species')
st.markdown('This bar chart compares the condition rate (as a percentage of throughput) across different animal species to identify which groups have higher incidence rates.')
species_stats = filtered.groupby('Species').agg(
    total_conditions=('NumberOfConditions','sum'),
    total_throughput=('Throughput','sum')
)
species_stats['rate'] = species_stats['total_conditions'] / species_stats['total_throughput'] * 100 
fig2, ax2 = plt.subplots() 
ax2.bar(species_stats.index, species_stats['rate']) 
ax2.set_title('Condition Rate by Species (% of Throughput)') 
st.pyplot(fig2) 

# Insight 3: Inspection Type Effectiveness (legend only, count-based percentages) 
st.subheader('Condition Distribution by Inspection Type')
st.markdown('This pie chart shows the share of detected conditions by inspection type, helping to assess ante-mortem vs post-mortem detection effectiveness.')
insp_stats = filtered.groupby('InspectionType').agg( 
    conditions=('NumberOfConditions', 'sum'), 
    throughput=('Throughput', 'sum') 
) 
# Calculate slice proportions based on condition counts 
total_conditions = insp_stats['conditions'].sum() 
inhab = insp_stats['conditions'] / total_conditions * 100  # percentages of total conditions 
fig3, ax3 = plt.subplots() 
# Draw pie without labels 
wedges, _ = ax3.pie( 
    insp_stats['conditions'], 
    labels=None, 
    startangle=90, 
    wedgeprops={'linewidth': 0.5, 'edgecolor': 'white'} 
) 
# Create legend with count-based percentage 
entry_labels = [f"{label}: {pct:.1f}%" for label, pct in zip(insp_stats.index, inhab)] 
ax3.legend( 
    wedges, 
    entry_labels, 
    title='Inspection Type', 
    loc='center left', 
    bbox_to_anchor=(1, 0.5), 
    fontsize=9 
) 
ax3.set_title('Condition Rate by Inspection Type') 
ax3.axis('equal')  # Equal aspect ratio ensures pie is circular 
st.pyplot(fig3) 

# Insight 4: Reporting Plant Coverage 
st.subheader('Reporting Plant Count Over Time')
st.markdown('This bar chart shows the number of plants reporting throughput each month, indicating reporting consistency and coverage.')
plants = filtered.groupby('YearMonth')['NumberOfThroughputPlants'].sum() 
fig4, ax4 = plt.subplots() 
ax4.bar(plants.index, plants.values) 
ax4.set_title('Number of Reporting Plants Over Time') 
ax4.set_xlabel('Month') 
ax4.set_ylabel('Plant Count') 
# Format x-axis to show only month names 
import matplotlib.dates as mdates 
ax4.xaxis.set_major_locator(mdates.MonthLocator()) 
ax4.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y')) 
fig4.autofmt_xdate() 
st.pyplot(fig4) 

# Insight 5: Normalized Condition Severity (enhanced clarity) 
st.subheader('Severity Distribution by Species')
st.markdown('This box plot with jittered points displays the distribution of condition severity (% of throughput) across species to reveal variability and outliers.')
labels = filtered['Species'].unique() 
bdata = [filtered[filtered['Species']==sp]['PercentageOfThroughput'] for sp in labels] 
fig5, ax5 = plt.subplots(figsize=(8, 4)) 
# Boxplot 
ax5.boxplot(bdata, labels=labels, patch_artist=True) 
# Jittered scatter for individual points 
import numpy as np 
for i, sp in enumerate(labels, start=1): 
 y = filtered[filtered['Species']==sp]['PercentageOfThroughput'] 
 x = np.random.normal(i, 0.05, size=len(y)) 
 ax5.scatter(x, y, alpha=0.6, s=10) 
# Formatting 
ax5.set_title('Distribution of Condition Severity by Species') 
ax5.set_xlabel('Species') 
ax5.set_ylabel('Percentage of Throughput') 
plt.setp(ax5.get_xticklabels(), rotation=45, ha='right') 
fig5.tight_layout() 
st.pyplot(fig5) 