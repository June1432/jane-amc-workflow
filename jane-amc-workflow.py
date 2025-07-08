# JANE PMS Dashboard v4.3 – Tabbed Wealth Platform with Client-Centric Navigation

import streamlit as st
import pandas as pd
import numpy as np
import numpy_financial as npf
import plotly.express as px
import datetime

st.set_page_config(page_title="JANE PMS Dashboard", layout="wide")

# ------------------------ Dummy Client Data Generator ------------------------ #

@st.cache_data
def get_client_data():
    num_clients = 50
    current_year = datetime.date.today().year

    start_dates = [datetime.date(np.random.randint(current_year - 3, current_year - 1), np.random.randint(1, 13), np.random.randint(1, 29)) for _ in range(num_clients)]
    end_dates = [sd + datetime.timedelta(days=np.random.randint(365, 1095)) for sd in start_dates]
    account_types = np.random.choice(["Resident", "NRE", "NRO"], size=num_clients)

    df = pd.DataFrame({
        "Client ID": [f"CID{i:03d}" for i in range(1, num_clients + 1)],
        "Name": [f"Client {i}" for i in range(1, num_clients + 1)],
        "Capital (₹ Lakhs)": np.random.randint(10, 500, size=num_clients),
        "Risk Profile": np.random.choice(["Low", "Medium", "High"], size=num_clients),
        "Strategy": np.random.choice(["Value", "Growth", "Momentum", "Balanced", "Arbitrage"], size=num_clients),
        "NAV": np.round(np.random.uniform(90, 180, num_clients), 2),
        "TWR (%)": np.round(np.random.uniform(-5, 25, num_clients), 2),
        "MWR (%)": np.round(np.random.uniform(-5, 30, num_clients), 2),
        "Start Date": start_dates,
        "End Date": end_dates,
        "Custodian": np.random.choice(["HDFC Bank", "ICICI Bank", "Axis Bank", "Kotak Bank"], size=num_clients),
        "Bank Account": [f"XXXX{i}{np.random.randint(1000, 9999)}" for i in range(num_clients)],
        "Account Type": account_types,
        "PEP": np.random.choice(["Yes", "No"], size=num_clients, p=[0.05, 0.95]),
        "PIS No": [f"PIS00{i}" if acct in ["NRE", "NRO"] else "" for i, acct in enumerate(account_types)],
        "Country": np.random.choice(["India", "UAE", "Singapore", "UK", "USA", "Canada"], size=num_clients),
        "FM": np.random.choice(["Rahul Khanna", "Sneha Desai", "Amit Verma"], size=num_clients),
        "RM": np.random.choice(["Ravi Mehta", "Neha Sharma"], size=num_clients),
        "SM": np.random.choice(["Rohit Sinha", "Kiran Shetty"], size=num_clients),
        "Distributor": np.random.choice(["Motilal", "NJ Wealth", "Groww"], size=num_clients)
    })

    df['Dividend Income (₹ Lakhs)'] = np.round(np.random.uniform(0.1, 5, num_clients), 2)
    df['Interest Income (₹ Lakhs)'] = np.round(np.random.uniform(0.05, 3, num_clients), 2)
    df['STCG (₹ Lakhs)'] = np.round(np.random.uniform(0, 10, num_clients), 2)
    df['LTCG (₹ Lakhs)'] = np.round(np.random.uniform(0, 15, num_clients), 2)
    df['TDS Rate (%)'] = np.random.choice([5, 10, 15, 20], size=num_clients, p=[0.4, 0.3, 0.2, 0.1])
    df['TDS Amount'] = np.round((df['Dividend Income (₹ Lakhs)'] + df['Interest Income (₹ Lakhs)']) * df['TDS Rate (%)'] / 100, 2)

    df['AML Risk Score'] = np.random.randint(1, 101, size=num_clients)
    df['Source of Wealth Verified'] = np.random.choice(["Yes", "No"], size=num_clients, p=[0.85, 0.15])
    df['PEP Status Date'] = df.apply(lambda row: datetime.date(np.random.randint(current_year - 2, current_year), np.random.randint(1, 13), np.random.randint(1, 29)) if row['PEP'] == 'Yes' else None, axis=1)
    df['Transaction Monitoring Flag'] = np.random.choice(["Green", "Yellow", "Red"], size=num_clients, p=[0.8, 0.15, 0.05])

    df['Third Party Txn Last 6M'] = np.random.choice(["Yes", "No"], size=num_clients, p=[0.2, 0.8])
    df['Third Party Relationship (Last Txn)'] = df.apply(lambda row: np.random.choice(["Spouse", "Parent", "Sibling", "Business Partner", "Other"]) if row['Third Party Txn Last 6M'] == 'Yes' else "N/A", axis=1)

    df['Initial Capital (₹ Lakhs)'] = df['Capital (₹ Lakhs)'] * np.random.uniform(0.5, 0.9, num_clients)
    df['Number of Tranches'] = np.random.randint(1, 6, size=num_clients)
    df['Investment Date'] = df['Start Date']
    df['Last Tranche Date'] = df.apply(lambda row: row['Investment Date'] + datetime.timedelta(days=np.random.randint(0, (row['Number of Tranches'] - 1) * 90)) if row['Number of Tranches'] > 1 else row['Investment Date'], axis=1)
    df['Tranche Details'] = df.apply(lambda row: f"{row['Number of Tranches']} payments" if row['Number of Tranches'] > 1 else "Single payment", axis=1)

    df['Asset Held Type'] = np.random.choice(["Equity", "Debt", "Hybrid", "Alternatives"], size=num_clients, p=[0.4, 0.3, 0.2, 0.1])
    df['Custody Reconciliation Status'] = np.random.choice(["Reconciled", "Pending", "Mismatch"], size=num_clients, p=[0.9, 0.08, 0.02])

    return df

# ------------------------ App Starts ------------------------ #
data = get_client_data()
st.title("JANE | PMS Enterprise Dashboard")

st.markdown("---")

# Create Tabs for Wealth Management Application
overview_tab, portfolio_tab, perf_tab, txn_tab, goals_tab, reports_tab, profile_tab, insights_tab, support_tab, tools_tab = st.tabs([
    "Dashboard", "Portfolio", "Performance", "Transactions", "Goals", "Reports & Statements",
    "Profile & Settings", "Insights & Research", "Support", "Tools & Calculators"
])

with overview_tab:
    st.subheader("Client Overview")
    st.metric("Total Clients", len(data))
    st.metric("Average NAV", round(data['NAV'].mean(), 2))
    st.metric("Total Capital Deployed (₹ Lakhs)", round(data['Capital (₹ Lakhs)'].sum(), 2))
    st.dataframe(data[['Client ID', 'Name', 'Capital (₹ Lakhs)', 'NAV', 'TWR (%)', 'Risk Profile', 'Strategy']])

with portfolio_tab:
    st.subheader("Investment Portfolio")
    st.dataframe(data[['Client ID', 'Name', 'Asset Held Type', 'Capital (₹ Lakhs)', 'NAV', 'Strategy']])
    st.plotly_chart(px.pie(data, names='Asset Held Type', title='Portfolio Allocation'))

with perf_tab:
    st.subheader("Performance Analytics")
    perf_cols = ['Client ID', 'Name', 'TWR (%)', 'MWR (%)', 'NAV', 'Risk Profile']
    st.dataframe(data[perf_cols])
    st.plotly_chart(px.scatter(data, x='TWR (%)', y='MWR (%)', color='Risk Profile', hover_name='Name'))

with txn_tab:
    st.subheader("Transaction Activity")
    st.dataframe(data[['Client ID', 'Name', 'Dividend Income (₹ Lakhs)', 'Interest Income (₹ Lakhs)', 'STCG (₹ Lakhs)', 'LTCG (₹ Lakhs)', 'TDS Amount', 'Third Party Txn Last 6M']])

with goals_tab:
    st.subheader("Client Goals (Simulated)")
    st.info("Goal tracking is in beta simulation mode.")

with reports_tab:
    st.subheader("Reports & Statements")
    st.info("Report download functionality coming soon.")

with profile_tab:
    st.subheader("Client Profile")
    st.dataframe(data[['Client ID', 'Name', 'Account Type', 'Bank Account', 'Country', 'PEP', 'Source of Wealth Verified']])

with insights_tab:
    st.subheader("Research & Insights")
    st.info("Insights and strategy commentary coming soon.")

with support_tab:
    st.subheader("Support")
    st.info("Chat, email, and RM contact integration coming soon.")

with tools_tab:
    st.subheader("Tools & Calculators")
    st.info("SIP, Retirement, and Tax calculators will be available soon.")
