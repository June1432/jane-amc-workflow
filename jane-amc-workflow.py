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
        if row['Capital (₹ Lakhs)'] > 0 and row['Start Date'] and row['End Date']:
            days_invested = (row['End Date'] - row['Start Date']).days
            if days_invested > 0:
                # Roughly simulate positive cash flows over the period
                # Simplistic: distribute NAV value as future cash flows after initial
                # For actual IRR, you'd need a series of actual cash inflows/outflows
                num_periods = int(days_invested / 30) if days_invested >= 30 else 1 # Convert days to months
                if num_periods == 0: num_periods = 1
                
                # Simulate gain based on TWR, then distribute it
                final_value = row['Capital (₹ Lakhs)'] * (1 + row['TWR (%)'] / 100)
                
                # A very simplistic cash flow: initial investment, then final value as one lump sum.
                # In reality, you'd have actual deposits/withdrawals.
                cashflows = [initial_investment] + [0] * (num_periods - 1) + [final_value]
                
                # Ensure cashflows has at least two elements and first is negative
                if len(cashflows) >= 2 and cashflows[0] < 0:
                    irr_val = npf.irr(cashflows)
                    return irr_val * 100 if np.isfinite(irr_val) else np.nan
                else:
                    return np.nan
            else:
                return np.nan # Cannot calculate for 0 days invested
        else:
            return np.nan
    except Exception:
        return np.nan # Return NaN for calculation errors

client_data = get_client_data()
client_data[['Sharpe', 'Treynor', 'Jensen']] = client_data.apply(calculate_ratios, axis=1)
client_data['IRR'] = client_data.apply(calculate_irr, axis=1)

# Calculate CAGR more accurately using Start Date and NAV/Capital
client_data['CAGR'] = client_data.apply(
    lambda row: ((row['NAV'] / row['Capital (₹ Lakhs)']) ** (1 / ((row['End Date'] - row['Start Date']).days / 365.25)) - 1) * 100
    if row['Capital (₹ Lakhs']) > 0 and (row['End Date'] - row['Start Date']).days > 0 else np.nan, axis=1
)

# Calculate TDS Amount
client_data['TDS Amount (₹ Lakhs)'] = np.round(
    (client_data['Dividend Income (₹ Lakhs)'] + client_data['Interest Income (₹ Lakhs)'] + 
     client_data['STCG (₹ Lakhs)'] + client_data['LTCG (₹ Lakhs)']) * (client_data['TDS Rate (%)'] / 100), 2
)

# Fill NaN values that might arise from calculations
client_data.fillna(0, inplace=True)

# Filter data based on sidebar dates
filtered_data = client_data[(client_data['Start Date'] >= start_filter) & (client_data['End Date'] <= end_filter)]

# ------------------------ Role-Based Views ------------------------ #

def fm_view():
    st.title("Fund Manager Dashboard")
    st.write("Overview of portfolio performance, strategy allocation, and key financial metrics, including investment patterns.")
    
    st.plotly_chart(px.line(filtered_data, x="Name", y=["NAV", "Capital (₹ Lakhs)"], title="NAV vs Total Capital by Client", hover_data=['TWR (%)', 'MWR (%)', 'CAGR', 'IRR']))
    st.plotly_chart(px.pie(filtered_data, names='Strategy', title='Strategy Allocation (by NAV)', values='NAV', hole=0.3))
    
    st.subheader("Client Performance & Investment Structure")
    st.dataframe(filtered_data[['Client ID', 'Name', 'Strategy', 'NAV', 'TWR (%)', 'MWR (%)', 'CAGR', 'Sharpe', 'Treynor', 'Jensen', 'IRR',
                                'Initial Capital (₹ Lakhs)', 'Number of Tranches', 'Last Tranche Date']].style.format({
        'NAV': "₹{:,.2f}", 'Capital (₹ Lakhs)': "₹{:,.2f}", 'Initial Capital (₹ Lakhs)': "₹{:,.2f}",
        'TWR (%)': "{:.2f}%", 'MWR (%)': "{:.2f}%", 'CAGR': "{:.2f}%", 'IRR': "{:.2f}%",
        'Sharpe': "{:.2f}", 'Treynor': "{:.2f}", 'Jensen': "{:.2f}",
        'Last Tranche Date': "%Y-%m-%d"
    }))

def rm_view():
    st.title("Relationship Manager Dashboard")
    st.write("Track client relationships, capital contributions, and individual client performance, with insight into their investment journey.")
    
    st.plotly_chart(px.bar(filtered_data, x="RM", y="Capital (₹ Lakhs)", color="RM", title="Total Capital Managed by Relationship Manager", text_auto=True))
    st.plotly_chart(px.bar(filtered_data, x="RM", y="Number of Tranches", color="RM", title="Average Tranches per Client by Relationship Manager", text_auto=True))
    
    st.subheader("Client Portfolio Summary")
    st.dataframe(filtered_data[['Client ID', 'Name', 'RM', 'Capital (₹ Lakhs)', 'Initial Capital (₹ Lakhs)', 'Number of Tranches', 'Last Tranche Date', 'TWR (%)', 'IRR', 'CAGR']].style.format({
        'Capital (₹ Lakhs)': "₹{:,.2f}", 'Initial Capital (₹ Lakhs)': "₹{:,.2f}",
        'TWR (%)': "{:.2f}%", 'IRR': "{:.2f}%", 'CAGR': "{:.2f}%",
        'Last Tranche Date': "%Y-%m-%d"
    }))

def sm_view():
    st.title("Service Manager Dashboard")
    st.write("Monitor client servicing scores, key client information, and operational details, including insights into transaction patterns.")
    df = filtered_data.copy()
    df['Servicing Score'] = np.random.randint(70, 100, len(df)) # Recalculate if not using cached data
    
    st.subheader("Client Servicing Overview")
    st.dataframe(df[['Client ID', 'Name', 'SM', 'Country', 'Bank Account', 'Servicing Score',
                     'Third Party Txn Last 6M', 'Third Party Relationship (Last Txn)']].style.format({
        'Servicing Score': "{:.0f}/100"
    }))
    
    st.plotly_chart(px.pie(df, names='Third Party Txn Last 6M', title='Third Party Transactions (Last 6 Months)', hole=0.3))


def distributor_view():
    st.title("Distributor Dashboard")
    st.write("Analyze business generated by distributors and their client base, including insights into capital contributions.")
    df_dist = filtered_data.groupby("Distributor").agg(
        {"Capital (₹ Lakhs)": "sum", "Client ID": "count", "Initial Capital (₹ Lakhs)": "sum", "Number of Tranches": "mean"}
    ).reset_index()
    df_dist = df_dist.rename(columns={'Client ID': 'Client Count', 'Number of Tranches': 'Avg Tranches'})

    st.plotly_chart(px.bar(df_dist, x="Distributor", y="Capital (₹ Lakhs)", color="Distributor", title="Total Business by Distributor", text_auto=True))
    st.plotly_chart(px.bar(df_dist, x="Distributor", y="Client Count", color="Distributor", title="Client Count by Distributor", text_auto=True))
    
    st.subheader("Distributor Performance Summary")
    st.dataframe(df_dist.style.format({
        'Capital (₹ Lakhs)': "₹{:,.2f}",
        'Initial Capital (₹ Lakhs)': "₹{:,.2f}",
        'Avg Tranches': "{:.1f}"
    }))

def operations_view():
    st.title("Operations Dashboard")
    st.write("Overview of operational statuses, client onboarding, custodian information, and key compliance flags for processing.")
    df = filtered_data.copy()
    df['Login Status'] = np.random.choice(["Created", "Pending Approval", "Active"], len(df), p=[0.1, 0.2, 0.7]) # More active clients

    st.subheader("Client Onboarding & Account Status")
    st.dataframe(df[['Client ID', 'Name', 'Custodian', 'Account Type', 'Login Status', 'AML Risk Score', 'Source of Wealth Verified', 'Custody Reconciliation Status']].style.format({
        'AML Risk Score': "{:.0f}"
    }))
    st.plotly_chart(px.pie(df, names='Login Status', title='Client Login Status Distribution', hole=0.3))
    
    st.subheader("Custody Reconciliation Overview")
    st.dataframe(df[['Client ID', 'Name', 'Custodian', 'Asset Held Type', 'Custody Reconciliation Status']])
    st.plotly_chart(px.pie(df, names='Custody Reconciliation Status', title='Custody Reconciliation Status', hole=0.3))


def compliance_view():
    st.title("Compliance Dashboard")
    st.write("Monitor regulatory adherence, AML flags, PEP clients, third-party transactions, and manage client complaints (SEBI SCORES).")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("PEP Clients", sum(filtered_data['PEP'] == 'Yes'))
    with col2:
        st.metric("High AML Risk Clients (Score > 75)", sum(filtered_data['AML Risk Score'] > 75))

    st.subheader("AML & Risk Monitoring")
    st.dataframe(filtered_data[['Client ID', 'Name', 'Risk Profile', 'AML Risk Score', 'Source of Wealth Verified', 'PEP', 'PEP Status Date', 'Transaction Monitoring Flag']].style.format({
        'AML Risk Score': "{:.0f}",
        'PEP Status Date': "%Y-%m-%d"
    }))
    
    st.plotly_chart(px.histogram(filtered_data, x='AML Risk Score', nbins=20, title='Distribution of AML Risk Scores'))
    st.plotly_chart(px.pie(filtered_data, names='Transaction Monitoring Flag', title='Transaction Monitoring Flags', hole=0.3))


    st.subheader("Third-Party Transaction Review")
    df_third_party = filtered_data[filtered_data['Third Party Txn Last 6M'] == 'Yes'].copy()
    if not df_third_party.empty:
        st.dataframe(df_third_party[['Client ID', 'Name', 'Third Party Txn Last 6M', 'Third Party Relationship (Last Txn)']])
        st.plotly_chart(px.pie(df_third_party, names='Third Party Relationship (Last Txn)', title='Types of Third-Party Relationships', hole=0.3))
    else:
        st.info("No third-party transactions recorded in the last 6 months for the selected period.")

    complaint_kpi = pd.DataFrame({
        'Client': filtered_data['Name'].sample(frac=0.5, replace=True).reset_index(drop=True), # Subset for complaints
        'Complaint Type': np.random.choice(['Delay', 'Disclosure', 'Mis-selling', 'Redemption', 'Others'], size=int(len(filtered_data)*0.5)),
        'Complaint Date': pd.to_datetime(pd.date_range(start=f'{current_year-1}-01-01', periods=int(len(filtered_data)*0.5))),
        'Resolved': np.random.choice(['Yes', 'No'], size=int(len(filtered_data)*0.5), p=[0.8, 0.2]),
        'Resolution Time (Days)': np.random.randint(1, 60, size=int(len(filtered_data)*0.5))
    })
    st.subheader("Complaint Summary (SEBI SCORES)")
    st.dataframe(complaint_kpi)
    st.plotly_chart(px.pie(complaint_kpi, names='Resolved', title='Complaint Resolution Status', hole=0.3))
    st.plotly_chart(px.bar(complaint_kpi, x='Complaint Type', title='Complaints by Type'))

    st.subheader("Regulatory Checks & PIS Details")
    st.dataframe(filtered_data[['Client ID', 'Name', 'PEP', 'Country', 'PIS No']])


def fund_accounting_view():
    st.title("Fund Accounting Dashboard")
    st.write("Detailed view of fund financials, gains, fees, NAV calculations, TDS, and custody reconciliation.")
    df = filtered_data.copy()
    
    df['Unrealized Gains (₹ Lakhs)'] = df['NAV'] - df['Capital (₹ Lakhs)']
    df['Realized Gains (₹ Lakhs)'] = df['STCG (₹ Lakhs)'] + df['LTCG (₹ Lakhs)'] # Sum of capital gains
    df['Accrued Fees (%)'] = np.round(np.random.uniform(0.25, 1.25, len(df)), 2)
    df['Management Fee (₹ Lakhs)'] = df['Capital (₹ Lakhs)'] * df['Accrued Fees (%)'] / 100
    df['GST (%)'] = 18.0
    df['GST on Fee (₹ Lakhs)'] = (df['Management Fee (₹ Lakhs)'] * df['GST (%)']) / 100
    df['NAV Date'] = datetime.date.today() # Use datetime.date for consistency

    st.plotly_chart(px.bar(df, x='Name', y='NAV', title='NAV Overview', hover_data=['Capital (₹ Lakhs)', 'Unrealized Gains (₹ Lakhs)']))
    st.plotly_chart(px.pie(df, names='Strategy', title='Strategy Distribution (by NAV)', values='NAV', hole=0.3))
    
    st.subheader("Fund Accounting Summary")
    st.dataframe(df[['Client ID', 'Name', 'Capital (₹ Lakhs)', 'Initial Capital (₹ Lakhs)', 'Number of Tranches', 'Last Tranche Date',
                     'NAV', 'Unrealized Gains (₹ Lakhs)', 'Realized Gains (₹ Lakhs)',
                     'Accrued Fees (%)', 'Management Fee (₹ Lakhs)', 'GST on Fee (₹ Lakhs)', 'NAV Date']].style.format({
        'Capital (₹ Lakhs)': "₹{:,.2f}", 'Initial Capital (₹ Lakhs)': "₹{:,.2f}",
        'NAV': "₹{:,.2f}", 'Unrealized Gains (₹ Lakhs)': "₹{:,.2f}", 'Realized Gains (₹ Lakhs)': "₹{:,.2f}",
        'Accrued Fees (%)': "{:.2f}%", 'Management Fee (₹ Lakhs)': "₹{:,.2f}", 'GST on Fee (₹ Lakhs)': "₹{:,.2f}",
        'NAV Date': "%Y-%m-%d", 'Last Tranche Date': "%Y-%m-%d"
    }))

    st.subheader("TDS and Income Overview")
    st.dataframe(df[['Client ID', 'Name', 'Dividend Income (₹ Lakhs)', 'Interest Income (₹ Lakhs)', 'STCG (₹ Lakhs)', 'LTCG (₹ Lakhs)',
                     'TDS Rate (%)', 'TDS Amount (₹ Lakhs)']].style.format({
        'Dividend Income (₹ Lakhs)': "₹{:,.2f}", 'Interest Income (₹ Lakhs)': "₹{:,.2f}",
        'STCG (₹ Lakhs)': "₹{:,.2f}", 'LTCG (₹ Lakhs)': "₹{:,.2f}",
        'TDS Rate (%)': "{:.2f}%", 'TDS Amount (₹ Lakhs)': "₹{:,.2f}"
    }))

    st.subheader("Custody Reconciliation Status")
    st.dataframe(df[['Client ID', 'Name', 'Custodian', 'Asset Held Type', 'Custody Reconciliation Status']].style.format({}))


def investor_view():
    st.title("Investor Dashboard")
    st.write("This is a simplified view for investors, providing key performance indicators and investment details. In a real application, only data for the logged-in investor would be displayed.")
    st.info("Currently showing aggregated data for demonstration. In a live system, this would be restricted to the logged-in investor's specific portfolio.")

    if filtered_data.empty:
        st.warning("No client data available for the selected date range.")
        return

    # In a real scenario, an investor would log in and their specific client ID would be known.
    # For demonstration, let's just pick a random client from the filtered data
    # Or, if you wanted to allow investor to pick for demo:
    # client_name_selection = st.selectbox("Select Your Client Name (Demo)", filtered_data['Name'].unique())
    # sample_client = filtered_data[filtered_data['Name'] == client_name_selection].iloc[0]
    sample_client = filtered_data.sample(1).iloc[0] # Pick a random client for demo purpose

    st.subheader(f"Portfolio Summary for {sample_client['Name']}")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Current NAV", f"₹{sample_client['NAV']:.2f} Lakhs")
    with col2:
        st.metric("Total Invested Capital", f"₹{sample_client['Capital (₹ Lakhs)']:.2f} Lakhs")
    with col3:
        st.metric("Overall TWR", f"{sample_client['TWR (%)']:.2f}%")

    st.subheader("Key Performance Indicators")
    st.dataframe(pd.DataFrame({
        'Metric': ['Time Weighted Return (TWR)', 'Money Weighted Return (MWR)', 'Compound Annual Growth Rate (CAGR)', 'Sharpe Ratio', 'Internal Rate of Return (IRR)'],
        'Value': [
            f"{sample_client['TWR (%)']:.2f}%",
            f"{sample_client['MWR (%)']:.2f}%",
            f"{sample_client['CAGR']:.2f}%",
            f"{sample_client['Sharpe']:.2f}",
            f"{sample_client['IRR']:.2f}%"
        ]
    }))

    st.subheader("Your Investment Details")
    st.dataframe(pd.DataFrame({
        'Detail': ['Strategy', 'Risk Profile', 'Initial Investment Date', 'Initial Capital', 'Number of Payments', 'Last Payment Date', 'Custodian', 'Asset Held Type'],
        'Value': [
            sample_client['Strategy'],
            sample_client['Risk Profile'],
            sample_client['Investment Date'].strftime("%Y-%m-%d"),
            f"₹{sample_client['Initial Capital (₹ Lakhs)']:.2f} Lakhs",
            sample_client['Number of Tranches'],
            sample_client['Last Tranche Date'].strftime("%Y-%m-%d"),
            sample_client['Custodian'],
            sample_client['Asset Held Type']
        ]
    }))
    
    st.subheader("Taxation Summary (TDS)")
    st.dataframe(pd.DataFrame({
        'Income Type': ['Dividend Income', 'Interest Income', 'Short Term Capital Gain', 'Long Term Capital Gain', 'Total TDS Deducted'],
        'Amount': [
            f"₹{sample_client['Dividend Income (₹ Lakhs)']:.2f} Lakhs",
            f"₹{sample_client['Interest Income (₹ Lakhs)']:.2f} Lakhs",
            f"₹{sample_client['STCG (₹ Lakhs)']:.2f} Lakhs",
            f"₹{sample_client['LTCG (₹ Lakhs)']:.2f} Lakhs",
            f"₹{sample_client['TDS Amount (₹ Lakhs)']:.2f} Lakhs"
        ]
    }))


# Main routing logic
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
elif role == "Investor":
    investor_view()
else:
    st.error("Invalid role or restricted access.")

st.markdown("---")
st.markdown("This dashboard reflects the internal operational and regulatory logic of a modern PMS platform aligned with SEBI PMS Regulations, RBI oversight, NCFE accounting principles, and SEBI SCORES grievance framework.")
