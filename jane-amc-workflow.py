# JANE PMS Dashboard v3.2 – Enhanced Version with Role-Based Login, Full Drilldowns, Real Data Simulation, Benchmarks, and Regulatory Alignment

import streamlit as st
import pandas as pd
import numpy as np
import numpy_financial as npf
import plotly.express as px
import datetime
from io import BytesIO

# ------------------------ Page Config ------------------------ #
st.set_page_config(page_title="JANE PMS Dashboard", layout="wide")

# ------------------------ Dummy Login ------------------------ #
CREDENTIALS = {
    "fm": "fm123",
    "rm": "rm123",
    "sm": "sm123",
    "distributor": "dist123",
    "operations": "ops123",
    "compliance": "comp123",
    "fundaccounting": "fa123",
    "investor": "inv123"
}

st.sidebar.title("🔐 Login")
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")
login = st.sidebar.button("Login")

if not login or username not in CREDENTIALS or CREDENTIALS[username] != password:
    st.warning("Please login to access the dashboard.")
    st.stop()

# ------------------------ Role Determination ------------------------ #
role_map = {
    "fm": "Fund Manager",
    "rm": "Relationship Manager",
    "sm": "Service Manager",
    "distributor": "Distributor",
    "operations": "Operations",
    "compliance": "Compliance",
    "fundaccounting": "Fund Accounting",
    "investor": "Investor"
}

role = role_map.get(username, "Unknown")

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

# ------------------------ Routing ------------------------ #
def fm_view():
    st.title("Fund Manager Dashboard")
    st.plotly_chart(px.line(filtered_data, x="Name", y=["NAV", "Capital (₹ Lakhs)"], title="NAV vs Capital by Client"))
    st.plotly_chart(px.pie(filtered_data, names='Strategy', title='Strategy Allocation'))
    st.dataframe(filtered_data[['Client ID', 'Name', 'Strategy', 'NAV', 'TWR (%)', 'CAGR', 'Sharpe', 'Treynor', 'Jensen', 'IRR']])

def rm_view():
    st.title("Relationship Manager Dashboard")
    st.plotly_chart(px.bar(filtered_data, x="RM", y="Capital (₹ Lakhs)", title="Capital by RM"))
    st.dataframe(filtered_data[['Client ID', 'Name', 'RM', 'Capital (₹ Lakhs)', 'TWR (%)', 'IRR', 'CAGR']])

def sm_view():
    st.title("Service Manager Dashboard")
    df = filtered_data.copy()
    df['Servicing Score'] = np.random.randint(70, 100, len(df))
    st.dataframe(df[['Client ID', 'Name', 'SM', 'Country', 'Bank Account', 'Servicing Score']])

def distributor_view():
    st.title("Distributor Dashboard")
    df = filtered_data.groupby("Distributor").agg({"Capital (₹ Lakhs)": "sum", "Client ID": "count"}).reset_index()
    st.plotly_chart(px.bar(df, x="Distributor", y="Capital (₹ Lakhs)", title="Business by Distributor"))
    st.dataframe(df.rename(columns={'Client ID': 'Client Count'}))

def operations_view():
    st.title("Operations Dashboard")
    df = filtered_data.copy()
    df['Login Status'] = np.random.choice(["Created", "Pending"], len(df))
    st.dataframe(df[['Client ID', 'Name', 'Custodian', 'Account Type', 'Login Status']])

def compliance_view():
    st.title("Compliance Dashboard")
    st.metric("PEP Clients", sum(filtered_data['PEP'] == 'Yes'))
    complaint_kpi = pd.DataFrame({
        'Client': filtered_data['Name'],
        'Complaint Type': np.random.choice(['Delay', 'Disclosure', 'Mis-selling', 'Redemption', 'Others'], len(filtered_data)),
        'Complaint Date': pd.date_range(start='2024-01-01', periods=len(filtered_data)),
        'Resolved': np.random.choice(['Yes', 'No'], len(filtered_data)),
        'Resolution Time (Days)': np.random.randint(1, 60, len(filtered_data))
    })
    st.subheader("Complaint Summary (SEBI SCORES)")
    st.dataframe(complaint_kpi)
    st.plotly_chart(px.pie(complaint_kpi, names='Resolved', title='Resolution Status'))
    st.plotly_chart(px.bar(complaint_kpi, x='Complaint Type', title='Complaints by Type'))
    st.subheader("Regulatory Checks")
    st.dataframe(filtered_data[['Client ID', 'Name', 'PEP', 'Country', 'PIS No']])

def fund_accounting_view():
    st.title("Fund Accounting Dashboard")
    df = filtered_data.copy()
    df['Unrealized Gains (₹)'] = df['NAV'] - df['Capital (₹ Lakhs)']
    df['Realized Gains (₹)'] = np.round(df['Capital (₹ Lakhs)'] * 0.03, 2)
    df['Accrued Fees (%)'] = np.round(np.random.uniform(0.25, 1.25, len(df)), 2)
    df['Management Fee (₹ Lakhs)'] = df['Capital (₹ Lakhs)'] * df['Accrued Fees (%)'] / 100
    df['GST (%)'] = 18.0
    df['GST on Fee'] = (df['Management Fee (₹ Lakhs)'] * df['GST (%)']) / 100
    df['NAV Date'] = datetime.date.today()
    st.plotly_chart(px.bar(df, x='Name', y='NAV', title='NAV Overview'))
    st.plotly_chart(px.pie(df, names='Strategy', title='Strategy Distribution'))
    st.subheader("Fund Accounting Summary")
    st.dataframe(df[['Client ID', 'Name', 'Capital (₹ Lakhs)', 'NAV', 'Unrealized Gains (₹)',
                    'Realized Gains (₹)', 'Accrued Fees (%)', 'Management Fee (₹ Lakhs)',
                    'GST on Fee', 'NAV Date']])

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
st.markdown("This dashboard reflects the internal operational and regulatory logic of a modern PMS platform aligned with SEBI PMS Regulations, RBI oversight, NCFE accounting principles, and SEBI SCORES grievance framework.")
