import streamlit as st
import pandas as pd


# sample data
data = {
    "Investor_Id": [i for i in range(1, 11)],
    "LastName": ["Smith", "Johnson", "Williams", "Jones", "Brown", "Davis",
                 "Miller", "Wilson", "Moore", "Taylor"],
    "Distrib_date": ["2019-01-15", "2019-02-20", "2019-03-25",
                     "2020-04-30", "2020-05-05", "2020-06-10",
                     "2021-07-15", "2021-08-20", "2021-09-25",
                     "2022-10-30"],
    "Distrib_Net": [15000.00, 20000.00, 25000.00, 30000.00, 35000.00, 
                    40000.00, 45000.00, 50000.00, 55000.00, 60000.00],
    "Investment": ["Bonds", "Stocks", "Real Estate", "Commodities", "Bonds",
                   "Stocks", "Real Estate", "Commodities", "Bonds", "Stocks"]
}


# create DataFrame
df = pd.DataFrame(data)

# Convert 'Distribution_date' to datetime format for calculations
df['Distrib_date'] = pd.to_datetime(df['Distrib_date'])

# Calculate 'Year' and 'Quarter' from 'Distribution_date'
df['Year'] = df['Distrib_date'].dt.year
df['Quarter'] = df['Distrib_date'].dt.quarter

st.title('BDK Services Group')
st.dataframe(df)

# unique items of select boxes
nameList = df['LastName'].drop_duplicates()
yearList = df['Year'].drop_duplicates()
quarterList = df['Quarter'].drop_duplicates()
investmentList = df['Investment'].drop_duplicates()

with st.sidebar:
    FilterInvestment = st.selectbox('Investment', investmentList)
    FilterLastName = st.selectbox('LastName', nameList)
    FilterYear = st.multiselect('Year',yearList)
    FilterQuarter = st.multiselect('Quarter', quarterList)

st.write('## Filtered')
filtered_df = df.loc[(df['Investment'] == FilterInvestment) & 
                    (df['LastName'] == FilterLastName) & 
                    (df['Year'].isin(FilterYear)) & 
                    (df['Quarter'].isin(FilterQuarter))]
st.write(filtered_df)