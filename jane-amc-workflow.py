# JANE PMS Dashboard v3.3 – Enhanced Version with Role-Based Login, Full Drilldowns, Real Data Simulation, Benchmarks, Regulatory Alignment, TDS, AML, Tranches, 3rd Party Txn, Custody

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

# Initialize session state for login
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None

st.sidebar.title("🔐 Login")

if not st.session_state.logged_in:
    username_input = st.sidebar.text_input("Username")
    password_input = st.sidebar.text_input("Password", type="password")
    login_button = st.sidebar.button("Login")

    if login_button:
        if username_input in CREDENTIALS and CREDENTIALS[username_input] == password_input:
            st.session_state.logged_in = True
            st.session_state.username = username_input
            st.sidebar.success(f"Welcome, {username_input}!")
            st.rerun() # Rerun to clear login fields and display content
        else:
            st.sidebar.error("Incorrect username or password. Please try again.")
            st.session_state.logged_in = False
            st.stop() # Stop execution if login fails

if not st.session_state.logged_in:
    st.warning("Please login to access the dashboard.")
    st.stop() # Stop further execution if not logged in

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

username = st.session_state.username
role = role_map.get(username, "Unknown")
st.sidebar.info(f"Logged in as: **{role}**")

# Date filters - only displayed after successful login
start_filter = st.sidebar.date_input("Start Date", value=datetime.date(2023, 1, 1))
end_filter = st.sidebar.date_input("End Date", value=datetime.date(2025, 12, 31))


# ------------------------ Dummy Data ------------------------ #
rms = ["Ravi Mehta", "Neha Sharma", "Arjun Iyer", "Divya Rao", "Kunal Singh"]
fms = ["Rahul Khanna", "Sneha Desai", "Amit Verma", "Priya Das", "Vinay Joshi"]
distributors = ["Motilal", "NJ Wealth", "ICICI Direct", "Axis Capital", "Groww"]
clients = [f"Client {i}" for i in range(1, 31)] # Increased client count

@st.cache_data
def get_client_data():
    num_clients = len(clients)
    current_year = datetime.date.today().year

    # Base dates for investment duration
    start_dates = [datetime.date(np.random.randint(current_year - 3, current_year -1), np.random.randint(1, 13), np.random.randint(1, 29)) for _ in range(num_clients)]
    end_dates = [sd + datetime.timedelta(days=np.random.randint(365, 1095)) for sd in start_dates] # 1-3 years later
    
    account_types = np.random.choice(["Resident", "NRE", "NRO"], size=num_clients)

    df = pd.DataFrame({
        "Client ID": [f"CID{i:03d}" for i in range(1, num_clients + 1)], # Formatted Client ID
        "Name": clients,
        "Capital (₹ Lakhs)": np.random.randint(10, 500, size=num_clients), # Total invested capital
        "Risk Profile": np.random.choice(["Low", "Medium", "High"], size=num_clients),
        "Strategy": np.random.choice(["Value", "Growth", "Momentum", "Balanced", "Arbitrage"], size=num_clients),
        "NAV": np.round(np.random.uniform(90, 180, num_clients), 2),
        "TWR (%)": np.round(np.random.uniform(-5, 25, num_clients), 2), # Wider range for returns
        "MWR (%)": np.round(np.random.uniform(-5, 30, num_clients), 2),
        "Start Date": start_dates, # Date when client account was opened/first investment
        "End Date": end_dates, # Simulated end date of investment horizon
        "Custodian": np.random.choice(["HDFC Bank", "ICICI Bank", "Axis Bank", "Kotak Bank"], size=num_clients),
        "Bank Account": [f"XXXX{i}{np.random.randint(1000, 9999)}" for i in range(num_clients)],
        "Account Type": account_types,
        "PEP": np.random.choice(["Yes", "No"], size=num_clients, p=[0.05, 0.95]), # Fewer PEP clients
        "PIS No": [f"PIS00{i}" if acct in ["NRE", "NRO"] else "" for i, acct in enumerate(account_types)],
        "Country": np.random.choice(["India", "UAE", "Singapore", "UK", "USA", "Canada"], size=num_clients),
        "FM": np.random.choice(fms, size=num_clients),
        "RM": np.random.choice(rms, size=num_clients),
        "SM": np.random.choice(["Rohit Sinha", "Kiran Shetty", "Priya Kulkarni"], size=num_clients),
        "Distributor": np.random.choice(distributors, size=num_clients)
    })

    # --- New Data Points ---

    # TDS related
    df['Dividend Income (₹ Lakhs)'] = np.round(np.random.uniform(0.1, 5, num_clients), 2)
    df['Interest Income (₹ Lakhs)'] = np.round(np.random.uniform(0.05, 3, num_clients), 2)
    df['STCG (₹ Lakhs)'] = np.round(np.random.uniform(0, 10, num_clients), 2) # Short Term Capital Gain
    df['LTCG (₹ Lakhs)'] = np.round(np.random.uniform(0, 15, num_clients), 2) # Long Term Capital Gain
    df['TDS Rate (%)'] = np.random.choice([5, 10, 15, 20], size=num_clients, p=[0.4, 0.3, 0.2, 0.1]) # Simulated TDS rates

    # AML related
    df['AML Risk Score'] = np.random.randint(1, 101, size=num_clients) # Score 1-100
    df['Source of Wealth Verified'] = np.random.choice(["Yes", "No"], size=num_clients, p=[0.85, 0.15])
    df['PEP Status Date'] = df.apply(lambda row: datetime.date(np.random.randint(current_year - 2, current_year), np.random.randint(1, 13), np.random.randint(1, 29)) if row['PEP'] == 'Yes' else None, axis=1)
    df['Transaction Monitoring Flag'] = np.random.choice(["Green", "Yellow", "Red"], size=num_clients, p=[0.8, 0.15, 0.05]) # Green: OK, Yellow: Review, Red: Alert

    # Third Party Transfer
    df['Third Party Txn Last 6M'] = np.random.choice(["Yes", "No"], size=num_clients, p=[0.2, 0.8])
    df['Third Party Relationship (Last Txn)'] = df.apply(
        lambda row: np.random.choice(["Spouse", "Parent", "Sibling", "Business Partner", "Other"]) if row['Third Party Txn Last 6M'] == 'Yes' else "N/A", axis=1
    )

    # Payments in Tranches
    df['Initial Capital (₹ Lakhs)'] = df['Capital (₹ Lakhs)'] * np.random.uniform(0.5, 0.9, num_clients) # Initial is less than total
    df['Number of Tranches'] = np.random.randint(1, 6, size=num_clients) # 1 to 5 tranches
    df['Investment Date'] = df['Start Date'] # Keeping original Start Date as first investment date
    df['Last Tranche Date'] = df.apply(
        lambda row: row['Investment Date'] + datetime.timedelta(days=np.random.randint(0, (row['Number of Tranches'] - 1) * 90)) if row['Number of Tranches'] > 1 else row['Investment Date'], axis=1
    )
    df['Tranche Details'] = df.apply(
        lambda row: f"{row['Number of Tranches']} payments" if row['Number of Tranches'] > 1 else "Single payment", axis=1
    )

    # Custody
    df['Asset Held Type'] = np.random.choice(["Equity", "Debt", "Hybrid", "Alternatives"], size=num_clients, p=[0.4, 0.3, 0.2, 0.1])
    df['Custody Reconciliation Status'] = np.random.choice(["Reconciled", "Pending", "Mismatch"], size=num_clients, p=[0.9, 0.08, 0.02])

    return df

# ------------------------ Calculations ------------------------ #
def calculate_ratios(row, rf=0.06, beta=1.1, mr=0.15): # Adjusted RF and Market Return for realism
    returns = row['TWR (%)'] / 100
    # Simulate volatility based on risk profile
    if row['Risk Profile'] == 'Low':
        volatility = np.random.uniform(0.05, 0.10)
    elif row['Risk Profile'] == 'Medium':
        volatility = np.random.uniform(0.10, 0.20)
    else:
        volatility = np.random.uniform(0.20, 0.35)

    sharpe = (returns - rf) / volatility if volatility != 0 else np.nan
    treynor = (returns - rf) / beta if beta != 0 else np.nan
    jensen = returns - (rf + beta * (mr - rf))
    return pd.Series({'Sharpe': sharpe, 'Treynor': treynor, 'Jensen': jensen})

def calculate_irr(row):
    try:
        # Simulate initial investment as negative, then monthly positive returns over a period
        # For simplicity, assume Capital is the total invested. We'll use this for IRR basis.
        initial_investment = -row['Capital (₹ Lakhs)']
        # Assume cash flows distributed over investment period or fixed for simulation
        # Using a more dynamic period based on investment dates
        if row['Capital (₹ Lakhs)'] > 0 and row['Start Date'] and
