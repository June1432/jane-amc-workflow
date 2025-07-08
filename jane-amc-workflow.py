# Folder structure for `jane_pms`

# ─── jane_pms/
# │
# ├── main.py                     # Entry point (Streamlit app router)
# ├── data/
# │   └── mock_data.py           # Simulated data (initially used instead of DB)
# ├── modules/
# │   ├── onboarding.py          # Client Digital Onboarding & KYC module
# │   ├── fee_calculation.py     # Fee Calculation & Billing module
# │   └── utils.py               # Shared utility functions
# ├── config/
# │   └── db_config.py           # DB connection setup (PostgreSQL ready)
# ├── static/
# │   └── sample_docs/           # Sample documents folder (PoI, PoA uploads)
# └── sql/
#     └── schema.sql             # PostgreSQL schema definitions

# ======================= main.py ==========================
import streamlit as st
from modules import onboarding, fee_calculation

st.set_page_config(page_title="JANE PMS", layout="wide")

st.sidebar.title("JANE PMS")
view = st.sidebar.radio("Select Module", [
    "Client Onboarding & KYC",
    "Fee Calculation & Billing"
])

if view == "Client Onboarding & KYC":
    onboarding.render()
elif view == "Fee Calculation & Billing":
    fee_calculation.render()

# ======================= modules/onboarding.py ==========================
import streamlit as st
from datetime import date

def render():
    st.title("📋 Client Digital Onboarding & KYC")
    st.subheader("Basic Details")

    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name")
        pan = st.text_input("PAN")
        aadhaar = st.text_input("Aadhaar Number")
        dob = st.date_input("Date of Birth")
    with col2:
        account_type = st.selectbox("Account Type", ["Resident", "NRE", "NRO"])
        country = st.selectbox("Country", ["India", "USA", "UAE", "UK", "Singapore"])
        bank = st.text_input("Bank Account No.")
        address = st.text_area("Address")

    st.subheader("AML / Compliance")
    pep = st.selectbox("PEP Status", ["Yes", "No"])
    source_of_wealth = st.text_input("Source of Wealth")
    aml_score = st.slider("AML Risk Score", 1, 100, 25)
    txn_flag = st.selectbox("Transaction Monitoring Flag", ["Green", "Yellow", "Red"])

    st.subheader("Document Upload")
    poi = st.file_uploader("Proof of Identity (PoI)")
    poa = st.file_uploader("Proof of Address (PoA)")
    pancard = st.file_uploader("PAN Card")
    bank_stmt = st.file_uploader("Bank Statement")

    st.subheader("Acknowledgments")
    mitc_ack = st.checkbox("I acknowledge the MITC document")
    fee_ack = st.checkbox("I acknowledge the Fee Annexure")

    status = st.radio("Application Status", ["Started", "Documents Uploaded", "Pending Approval", "Approved"])

    if st.button("Submit Onboarding"):
        st.success(f"Client {name} onboarded successfully (Simulated)")

# ======================= modules/fee_calculation.py ==========================
import streamlit as st

def calc_management_fee(aum):
    if aum < 500:  # AUM < 5 Cr
        rate = 0.015
    elif aum < 1000:  # 5–10 Cr
        rate = 0.012
    else:
        rate = 0.01
    return aum * rate

def calc_performance_fee(aum, growth, hurdle=0.1):
    profit = aum * (growth - hurdle) if growth > hurdle else 0
    return profit * 0.10

def calc_gst(fee):
    return fee * 0.18

def render():
    st.title("💸 Fee Calculation Tool")

    aum = st.number_input("AUM (₹ Lakhs)", min_value=0.0)
    growth = st.slider("Annual Portfolio Growth (%)", 0.0, 50.0, 10.0) / 100

    mgmt_fee = calc_management_fee(aum)
    perf_fee = calc_performance_fee(aum, growth)
    gst = calc_gst(mgmt_fee + perf_fee)
    total = mgmt_fee + perf_fee + gst

    st.metric("Management Fee", f"₹ {mgmt_fee:.2f} Lakhs")
    st.metric("Performance Fee", f"₹ {perf_fee:.2f} Lakhs")
    st.metric("GST (18%)", f"₹ {gst:.2f} Lakhs")
    st.success(f"Total Fee Payable: ₹ {total:.2f} Lakhs")

# ======================= sql/schema.sql ==========================
-- Table: clients
CREATE TABLE clients (
    id SERIAL PRIMARY KEY,
    name TEXT,
    pan TEXT,
    aadhaar TEXT,
    dob DATE,
    account_type TEXT,
    country TEXT,
    bank_account TEXT,
    address TEXT,
    pep TEXT,
    source_of_wealth TEXT,
    aml_score INT,
    txn_flag TEXT,
    mitc_ack BOOLEAN,
    fee_ack BOOLEAN,
    status TEXT
);

-- Table: fee_calculations
CREATE TABLE fee_calculations (
    id SERIAL PRIMARY KEY,
    client_id INT REFERENCES clients(id),
    aum NUMERIC,
    growth NUMERIC,
    mgmt_fee NUMERIC,
    perf_fee NUMERIC,
    gst NUMERIC,
    total_fee NUMERIC,
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
