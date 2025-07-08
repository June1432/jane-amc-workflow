# JANE PMS Dashboard v3 - Enhanced Version with Ops, Compliance, Fund Accounting

import streamlit as st
import pandas as pd
import numpy as np
import numpy_financial as npf
import plotly.express as px
import datetime
from io import BytesIO

# ------------------------ Page Config ------------------------ #
st.set_page_config(page_title="JANE PMS Dashboard", layout="wide")

# ------------------------ Sidebar ------------------------ #
st.sidebar.title("JANE PMS Dashboard")
role = st.sidebar.radio("Select Role", [
    "Fund Manager", "Relationship Manager", "Service Manager",
    "Distributor", "Operations", "Compliance", "Fund Accounting"])

start_filter = st.sidebar.date_input("Start Date", value=datetime.date(2023, 1, 1))
end_filter = st.sidebar.date_input("End Date", value=datetime.date(2025, 12, 31))

# ------------------------ Dummy Data ------------------------ #
rms = ["Ravi Mehta", "Neha Sharma", "Arjun Iyer", "Divya Rao", "Kunal Singh"]
fms = ["Rahul Khanna", "Sneha Desai", "Amit Verma", "Priya Das", "Vinay Joshi"]
distributors = ["Motilal", "NJ Wealth", "ICICI Direct", "Axis Capital", "Groww"]
clients = [f"Client {i}" for i in range(1, 11)]

@st.cache_data
def get_client_data():
    start_dates = [datetime.date(2023, 1, i+1) for i in range(10)]
    end_dates = [datetime.date(2025, 1, i+1) for i in range(10)]
    account_types = np.random.choice(["Resident", "NRE", "NRO"], size=10)
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
        "Account Type": account_types,
        "PEP": np.random.choice(["Yes", "No"], size=10),
        "PIS No": [f"PIS00{i}" if acct in ["NRE", "NRO"] else "" for i, acct in enumerate(account_types)],
        "Country": np.random.choice(["India", "UAE", "Singapore", "UK"], size=10),
        "FM": np.random.choice(fms, size=10),
        "RM": np.random.choice(rms, size=10),
        "SM": np.random.choice(["Rohit Sinha", "Kiran Shetty"], size=10),
        "Distributor": np.random.choice(distributors, size=10)
    })

# ------------------------ Calculations ------------------------ #
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
client_data['CAGR'] = ((client_data['NAV'] / client_data['Capital (₹ Lakhs)']) ** (1/2) - 1) * 100
filtered_data = client_data[(client_data['Start Date'] >= start_filter) & (client_data['End Date'] <= end_filter)]

# ------------------------ Excel Export ------------------------ #
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Data')
    return output.getvalue()

# ------------------------ Views ------------------------ #
def fm_view():
    selected = st.selectbox("Select Fund Manager:", fms)
    df = filtered_data[filtered_data['FM'] == selected]
    st.title(f"Fund Manager | {selected}")
    st.metric("Total AUM (₹ Cr)", f"{df['Capital (₹ Lakhs)'].sum() / 100:.2f}")
    st.plotly_chart(px.bar(df, x="Name", y="Capital (₹ Lakhs)", title="Client Capital"))
    st.plotly_chart(px.pie(df, names='Strategy', title='Strategy Allocation'))
    st.plotly_chart(px.line(df, x='Name', y=['NAV'], title='NAV Trend'))
    st.download_button("Download FM Data", data=to_excel(df), file_name="FM_Report.xlsx")

def rm_view():
    selected = st.selectbox("Select RM:", rms)
    df = filtered_data[filtered_data['RM'] == selected]
    st.title(f"Relationship Manager | {selected}")
    st.metric("Total Clients", len(df))
    st.plotly_chart(px.pie(df, names='Risk Profile', title='Risk Profile Distribution'))
    st.dataframe(df[["Client ID", "Name", "Strategy", "TWR (%)", "CAGR", "IRR"]])
    st.download_button("Download RM Data", data=to_excel(df), file_name="RM_Report.xlsx")

def sm_view():
    selected = st.selectbox("Select SM:", ["Rohit Sinha", "Kiran Shetty"])
    df = filtered_data[filtered_data['SM'] == selected]
    st.title(f"Service Manager | {selected}")
    st.metric("Client Base Size", len(df))
    st.plotly_chart(px.bar(df, x="Country", title="Geographic Spread"))
    st.dataframe(df[["Client ID", "Name", "Country", "Custodian", "Bank Account"]])
    st.download_button("Download SM Data", data=to_excel(df), file_name="SM_Report.xlsx")

def distributor_view():
    selected = st.selectbox("Select Distributor:", distributors)
    df = filtered_data[filtered_data['Distributor'] == selected]
    st.title(f"Distributor | {selected}")
    st.plotly_chart(px.bar(df, x='Name', y='Capital (₹ Lakhs)', title="Capital Brought In"))
    st.plotly_chart(px.pie(df, names='Strategy', title='Client Strategy Split'))
    st.dataframe(df[["Client ID", "Name", "Country", "Capital (₹ Lakhs)"]])
    st.download_button("Download Distributor Data", data=to_excel(df), file_name="Distributor_Report.xlsx")

def operations_view():
    st.title("Operations Team Dashboard")
    st.metric("Total Accounts Opened", len(filtered_data))
    onboarding_kpi = pd.DataFrame({
        'Client': filtered_data['Name'],
        'Login Created': np.random.choice(["Yes", "No"], size=len(filtered_data))
    })
    st.dataframe(onboarding_kpi)

def compliance_view():
    st.title("Compliance Team Dashboard")
    st.metric("PEP Clients", sum(filtered_data['PEP'] == 'Yes'))
    st.plotly_chart(px.pie(filtered_data, names='Country', title='Country Risk Distribution'))
    st.dataframe(filtered_data[['Client ID', 'Name', 'PEP', 'Country', 'PIS No']])

def fund_accounting_view():
    st.title("Fund Accounting Dashboard")
    df = filtered_data
    df['Brokerage (%)'] = np.round(np.random.uniform(0.25, 0.75, len(df)), 2)
    df['Billing Forecast (₹ Lakhs)'] = df['Capital (₹ Lakhs)'] * df['Brokerage (%)'] / 100
    st.plotly_chart(px.line(df, x='Name', y='NAV', title='NAV Movement'))
    st.dataframe(df[['Client ID', 'Name', 'Capital (₹ Lakhs)', 'NAV', 'Brokerage (%)', 'Billing Forecast (₹ Lakhs)']])

# ------------------------ Routing ------------------------ #
if role == "Fund Manager":
    fm_view()
elif role == "Relationship Manager":
    rm_view()
elif role == "Service Manager":
    sm_view()
elif role == "Distributor":
    distributor_view()
elif role == "Operations":
    operations_view()
elif role == "Compliance":
    compliance_view()
elif role == "Fund Accounting":
    fund_accounting_view()

st.markdown("---")
st.markdown("This dashboard simulates a real-time PMS application aligned with SEBI PMS Regulations 2020 and RBI norms.")
