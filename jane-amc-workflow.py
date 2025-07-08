import streamlit as st
import graphviz

st.set_page_config(page_title="AMC Workflow | JANE", layout="wide")
st.title("JANE | AMC Lifecycle Workflow")
st.markdown("This end-to-end flow illustrates client onboarding, fund allocation, operations, compliance, and exit—designed as per SEBI PMS Regulations and RBI norms.")

st.subheader("⚙️ Institutional AMC Workflow")

# Graphviz Diagram
workflow = graphviz.Digraph(format="png")
workflow.attr(rankdir='LR', bgcolor='white')

# Stage 1: Prospect & Sales
workflow.node("Prospect", "Prospect (HNI / Institution)", shape="box")
workflow.node("LeadMgmt", "Sales / RM / Distributor", shape="box")
workflow.edge("Prospect", "LeadMgmt", label="Lead → Qualification")
workflow.edge("LeadMgmt", "Compliance", label="KYC / FATCA / PEP Check")

# Stage 2: Onboarding & Legal
workflow.node("Compliance", "Compliance & Legal Review", shape="box")
workflow.node("OpsTeam", "Operations Team", shape="box")
workflow.edge("Compliance", "OpsTeam", label="Approve Client Setup")
workflow.edge("OpsTeam", "Login", label="Client ID + Dashboard")
workflow.node("Login", "Login Created (Investor Portal)", shape="box")

# Stage 3: Fund Deployment
workflow.node("FundMgr", "Fund Manager", shape="box")
workflow.node("Desk", "Trade Desk", shape="box")
workflow.edge("Login", "FundMgr", label="Capital + Risk Profile")
workflow.edge("FundMgr", "Desk", label="Asset Strategy → Order")
workflow.edge("Desk", "OpsTeam", label="Units + ISIN Allotment")

# Stage 4: Reporting & Compliance
workflow.node("Reporting", "Performance Reporting", shape="box")
workflow.node("Investor", "Investor / Client", shape="box")
workflow.edge("OpsTeam", "Reporting", label="NAV + Returns + IRR")
workflow.edge("Reporting", "Investor", label="App / PDF Reports")

# Stage 5: Lifecycle Changes
workflow.node("RMServicing", "Relationship Manager", shape="box")
workflow.edge("Investor", "RMServicing", label="Top-up / Switch / Exit")
workflow.edge("RMServicing", "FundMgr", label="Trigger Rebalance")
workflow.edge("FundMgr", "Desk")
workflow.edge("Desk", "OpsTeam")
workflow.edge("OpsTeam", "Reporting")

# Stage 6: Exit & Payout
workflow.node("Finance", "Finance & Custody", shape="box")
workflow.node("Closure", "Exit + Final Closure", shape="box")
workflow.edge("Investor", "Closure", label="Redemption Request")
workflow.edge("Closure", "OpsTeam", label="Liquidate + Confirm")
workflow.edge("OpsTeam", "Finance", label="Fund Release")
workflow.edge("Finance", "Investor", label="Bank Transfer + Exit Note")

# Display Diagram
st.graphviz_chart(workflow, use_container_width=True)

st.markdown("---")
st.markdown("© JANE PMS – Built in compliance with **SEBI PMS Regulations**, **RBI KYC / PMLA rules**, and **internal AMC protocols**.")
