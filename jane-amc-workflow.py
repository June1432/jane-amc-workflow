# JANE PMS Dashboard v3 - Enhanced Version with Ops, Compliance, Fund Accounting (Corrected)

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

# ------------------------ Compliance View ------------------------ #
def compliance_view():
    st.title("Compliance Team Dashboard")
    st.metric("PEP Clients", sum(filtered_data['PEP'] == 'Yes'))

    complaint_kpi = pd.DataFrame({
        'Client': filtered_data['Name'],
        'Complaint Type': np.random.choice(['Delay', 'Disclosure', 'Mis-selling', 'Redemption', 'Others'], len(filtered_data)),
        'Complaint Date': pd.date_range(start='2024-01-01', periods=len(filtered_data)),
        'Resolved': np.random.choice(['Yes', 'No'], len(filtered_data)),
        'Resolution Time (Days)': np.random.randint(1, 60, len(filtered_data))
    })

    st.subheader("Complaint Summary (as per SEBI SCORES)")
    st.dataframe(complaint_kpi)
    st.plotly_chart(px.pie(complaint_kpi, names='Resolved', title='Resolution Status'))
    st.plotly_chart(px.bar(complaint_kpi, x='Complaint Type', title='Complaints by Type'))
    
    st.subheader("Client Regulatory Flags")
    st.dataframe(filtered_data[['Client ID', 'Name', 'PEP', 'Country', 'PIS No']])

# ------------------------ Fund Accounting View ------------------------ #
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

    st.plotly_chart(px.bar(df, x='Name', y='NAV', title='Latest NAV by Client'))
    st.plotly_chart(px.pie(df, names='Strategy', title='Allocation by Strategy'))

    st.subheader("Valuation & Fee Snapshot")
    st.dataframe(df[['Client ID', 'Name', 'Capital (₹ Lakhs)', 'NAV', 'Unrealized Gains (₹)',
                    'Realized Gains (₹)', 'Accrued Fees (%)', 'Management Fee (₹ Lakhs)',
                    'GST on Fee', 'NAV Date']])

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
st.markdown("This dashboard simulates a real-time PMS application aligned with SEBI PMS Regulations 2020, RBI norms, and AMFI SCORES framework.")
