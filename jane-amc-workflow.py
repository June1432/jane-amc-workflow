import streamlit as st
import pandas as pd
import numpy as np
import datetime
from io import BytesIO
import numpy_financial as npf

st.set_page_config(page_title="JANE PMS Dashboard", layout="wide")

st.sidebar.title("Select Role View")
role = st.sidebar.selectbox("User Role:", ["Fund Manager", "Relationship Manager", "Service Manager", "Distributor"])

st.sidebar.markdown("### Filter by Date Range")
start_filter = st.sidebar.date_input("Start Date", value=datetime.date(2023, 1, 1))
end_filter = st.sidebar.date_input("End Date", value=datetime.date(2025, 12, 31))

rms = ["Ravi Mehta", "Neha Sharma", "Arjun Iyer", "Divya Rao", "Kunal Singh"]
fms = ["Rahul Khanna", "Sneha Desai", "Amit Verma", "Priya Das", "Vinay Joshi"]
distributors = ["Motilal", "NJ Wealth", "ICICI Direct", "Axis Capital", "Groww"]
clients = [f"Client {i}" for i in range(1, 11)]

@st.cache_data
def get_client_data():
    start_dates = [datetime.date(2023, 1, i+1) for i in range(10)]
    end_dates = [datetime.date(2025, 1, i+1) for i in range(10)]
    return pd.DataFrame({
        "Client ID": [f"CID{i}" for i in range(1, 11)],
        "Name": clients,
        "Capital (₹ Lakhs)": np.random.randint(10, 100, size=10),
        "Risk Profile": np.random.choice(["Low", "Medium", "High"], size=10),
        "Strategy": np.random.choice(["Value", "Growth", "Momentum"], size=10),
        "NAV": np.round(np.random.uniform(90, 150, 10), 2),
        "TWR (%)": np.round(np.random.uniform(-2, 15, 10), 2),
        "MWR (%)": np.round(np.random.uniform(-2, 18, 10), 2),
        "Start Date": start_dates,
        "End Date": end_dates,
        "Custodian": np.random.choice(["HDFC Bank", "ICICI Bank"], size=10),
        "Bank Account": [f"XXXX{i}1234" for i in range(10)],
        "PEP": np.random.choice(["Yes", "No"], size=10),
        "PIS No": [f"PIS00{i}" for i in range(10)],
        "Country": np.random.choice(["India", "UAE", "Singapore", "UK"], size=10),
        "FM": np.random.choice(fms, size=10),
        "RM": np.random.choice(rms, size=10),
        "SM": np.random.choice(["Rohit Sinha", "Kiran Shetty"], size=10),
        "Distributor": np.random.choice(distributors, size=10)
    })

def calculate_ratios(row, rf=0.05, beta=1.0, mr=0.12):
    returns = row['TWR (%)'] / 100
    volatility = 0.12
    sharpe = (returns - rf) / volatility
    treynor = (returns - rf) / beta
    jensen = returns - (rf + beta * (mr - rf))
    return pd.Series({'Sharpe': sharpe, 'Treynor': treynor, 'Jensen': jensen})

def calculate_irr(row):
    try:
        cashflows = [-row['Capital (₹ Lakhs)']] + [row['NAV'] / 12] * 24
        return npf.irr(cashflows)
    except:
        return None

client_data = get_client_data()
client_data[['Sharpe', 'Treynor', 'Jensen']] = client_data.apply(calculate_ratios, axis=1)
client_data['IRR'] = client_data.apply(calculate_irr, axis=1)

filtered_data = client_data[(client_data['Start Date'] >= start_filter) & (client_data['End Date'] <= end_filter)]

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    processed_data = output.getvalue()
    return processed_data

if role == "Fund Manager":
    selected_fm = st.selectbox("Select Fund Manager:", fms)
    fm_clients = filtered_data[filtered_data['FM'] == selected_fm]
    if fm_clients.empty:
        st.warning("No clients found for this Fund Manager in the selected date range.")
        st.stop()
    st.title(f"Fund Manager View - {selected_fm}")
    col1, col2 = st.columns(2)
    col1.metric("Total AUM (₹ Cr)", f"{fm_clients['Capital (₹ Lakhs)'].sum() / 100:.2f}")
    col2.metric("Benchmark Return (Nifty 1Y)", "12.0%")
    st.subheader("Capital by Client")
    st.bar_chart(fm_clients.set_index("Name")["Capital (₹ Lakhs)"])
    st.subheader("Strategy Breakdown")
    st.bar_chart(fm_clients['Strategy'].value_counts())
    st.subheader("NAV vs Benchmark")
    benchmark = pd.Series([120]*len(fm_clients), index=fm_clients['Name'])
    combined_nav = pd.DataFrame({"NAV": fm_clients['NAV'].values, "Benchmark": benchmark.values}, index=fm_clients['Name'])
    st.line_chart(combined_nav)
    st.download_button("Download FM Data (Excel)", data=to_excel(fm_clients), file_name="FM_Report.xlsx")

elif role == "Relationship Manager":
    selected_rm = st.selectbox("Select RM:", rms)
    rm_clients = filtered_data[filtered_data['RM'] == selected_rm]
    if rm_clients.empty:
        st.warning("No clients found for this RM in the selected date range.")
        st.stop()
    st.title(f"Relationship Manager View - {selected_rm}")
    st.subheader("Risk Profile Distribution")
    st.bar_chart(rm_clients['Risk Profile'].value_counts())
    st.subheader("Capital by Client")
    st.bar_chart(rm_clients.set_index("Name")["Capital (₹ Lakhs)"])
    st.subheader("Assigned Clients")
    st.dataframe(rm_clients[["Client ID", "Name", "Strategy", "Risk Profile", "TWR (%)", "NAV", "IRR"]])
    st.download_button("Download RM Data (Excel)", data=to_excel(rm_clients), file_name="RM_Report.xlsx")

elif role == "Service Manager":
    selected_sm = st.selectbox("Select SM:", ["Rohit Sinha", "Kiran Shetty"])
    sm_clients = filtered_data[filtered_data['SM'] == selected_sm]
    if sm_clients.empty:
        st.warning("No clients found for this SM in the selected date range.")
        st.stop()
    st.title(f"Service Manager View - {selected_sm}")
    st.subheader("Client Country Breakdown")
    st.bar_chart(sm_clients['Country'].value_counts())
    st.subheader("Client Details")
    st.dataframe(sm_clients[["Client ID", "Name", "Custodian", "Bank Account", "PEP", "PIS No", "Country"]])
    st.download_button("Download SM Data (Excel)", data=to_excel(sm_clients), file_name="SM_Report.xlsx")

elif role == "Distributor":
    selected_dist = st.selectbox("Select Distributor:", distributors)
    dist_clients = filtered_data[filtered_data['Distributor'] == selected_dist]
    if dist_clients.empty:
        st.warning("No clients found for this Distributor in the selected date range.")
        st.stop()
    st.title(f"Distributor View - {selected_dist}")
    st.subheader("Strategy Breakdown")
    st.bar_chart(dist_clients['Strategy'].value_counts())
    st.subheader("Client List")
    st.dataframe(dist_clients[["Client ID", "Name", "Capital (₹ Lakhs)", "Country"]])
    st.download_button("Download Distributor Data (Excel)", data=to_excel(dist_clients), file_name="Distributor_Report.xlsx")

st.markdown("---")
st.markdown("This dashboard is a simulated proof of concept. Data aligns with SEBI PMS 2020 regulations and internal audit principles.")
