# frontend/app.py
import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px

# Set browser tab configurations
st.set_page_config(
    page_title="ASOC Real-Time AI Intelligence Command",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ Autonomous Security Operations Center (ASOC)")
st.markdown("### Real-Time Security Log Stream & AI Threat Analytics Dashboard")
st.markdown("---")

# Function to read directly from your local SQL database archive file
def fetch_security_data():
    try:
        # Connect to your existing SQLite database file
        conn = sqlite3.connect("security_archive.db")
        
        # Read the table directly into a powerful Pandas DataFrame matrix
        # Removing the 'timestamp' dependency to avoid SQL crashing
        query = "SELECT id, ip_address, threat_score, security_status, incident_log FROM security_alerts ORDER BY id DESC"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        # Returns an empty dataframe if the table hasn't been created yet
        return pd.DataFrame()

# Fetch latest database state
df = fetch_security_data()

if df.empty:
    st.warning("⚠️ No security alerts found in the SQL database archive yet. Fire some request payloads via your FastAPI endpoint to generate live metrics!")
else:
    # 📈 PHASE A: High-Level Metric Layout Summary
    total_logs = len(df)
    critical_threats = len(df[df['security_status'] == 'CRITICAL_THREAT_DETECTED'])
    safe_traffic = len(df[df['security_status'] == 'SAFE_TRAFFIC'])
    avg_threat_score = df['threat_score'].mean()

    # Create four parallel metric column cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Total Ingested Logs", value=total_logs)
    with col2:
        st.metric(label="🚨 Critical Incidents", value=critical_threats)
    with col3:
        st.metric(label="Safe Traffic Streams", value=safe_traffic)
    with col4:
        st.metric(label="Avg Threat Index Score", value=f"{round(avg_threat_score, 1)}%")

    st.markdown("---")

    # 📊 PHASE B: Interactive Chart Visualizations & Advanced Leaderboard
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader("⚠️ Threat Distribution Breakdown")
        fig_pie = px.pie(df, names='security_status', color='security_status',
                         color_discrete_map={'CRITICAL_THREAT_DETECTED': '#FF4B4B', 'SUSPICIOUS_ANOMALY': '#FFA500', 'SAFE_TRAFFIC': '#00CC96'})
        st.plotly_chart(fig_pie, use_container_width=True)

    with chart_col2:
        st.subheader("👑 Top IP Threat Leaderboard")
        # Aggregating records to count occurrences of bad actors from your real data matrix
        leaderboard = (
            df.groupby('ip_address')
            .size()
            .reset_index(name='Total Alerts Triggered')
            .sort_values(by='Total Alerts Triggered', ascending=False)
            .head(5)
        )
        st.dataframe(leaderboard, use_container_width=True, hide_index=True)
        st.caption("Identifies offending source network origins generating maximum metrics variations.")

    st.markdown("---")

    # 📋 PHASE C: Structured Historical Audit Ledger Table
    st.subheader("🕵️ Live System Audit Log Ledger")
    st.dataframe(
        df[['id', 'ip_address', 'threat_score', 'security_status', 'incident_log']], 
        use_container_width=True,
        hide_index=True
    )

# 🔄 Quick Dashboard Refresh Control
st.sidebar.markdown("## ⚙️ Control Panel")
if st.sidebar.button("🔄 Sync Database Records", use_container_width=True):
    st.rerun()