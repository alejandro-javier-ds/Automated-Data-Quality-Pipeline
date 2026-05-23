import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import config

st.set_page_config(page_title="Enterprise Data Quality", layout="wide")

def get_sql_engine():
    conn_str = f"mssql+pyodbc://@{config.SERVER_NAME}/{config.DATABASE_NAME}?driver=ODBC+Driver+17+for+SQL+Server&Trusted_Connection=yes"
    return create_engine(conn_str)

@st.cache_data(ttl=60)
def fetch_processed_data():
    engine = get_sql_engine()
    try:
        df_clean = pd.read_sql("SELECT * FROM Clean_Sales", engine)
        df_quarantine = pd.read_sql("SELECT * FROM Quarantine_Sales", engine)
        return df_clean, df_quarantine
    except Exception as e:
        return None, None

def main():
    st.markdown("""
        <style>
        .main-header { font-size: 2.2rem; font-weight: 700; color: #1e3a8a; margin-bottom: 0;}
        .sub-header { font-size: 1.1rem; color: #64748b; margin-bottom: 2rem;}
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<p class="main-header">Automated Data Quality & Governance</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Single Source of Truth (SSOT) Audit & Anomaly Detection Motor</p>', unsafe_allow_html=True)

    df_clean, df_quarantine = fetch_processed_data()

    if df_clean is None and df_quarantine is None:
        st.error("CRITICAL ERROR: Unable to establish connection to SQL Server or tables do not exist.")
        st.stop()

    total_clean = len(df_clean)
    total_quarantine = len(df_quarantine)
    total_records = total_clean + total_quarantine
    
    health_score = (total_clean / total_records) * 100 if total_records > 0 else 0

    with st.sidebar:
        st.title("Control Panel")
        st.markdown("---")
        
        st.subheader("Data Synchronization")
        if st.button("Refresh Analytics", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
            
        st.markdown("---")
        st.info("System strictly operates in Read-Only mode. All ETL and Quality Rule evaluations are handled asynchronously by the backend engine.")

    if health_score >= 90:
        st.success(f"SYSTEM STATUS: OPTIMAL | Data Reliability Index: {health_score:.1f}%")
    elif health_score >= 70:
        st.warning(f"SYSTEM STATUS: DEGRADED | Data Reliability Index: {health_score:.1f}% (Audit required)")
    else:
        st.error(f"SYSTEM STATUS: CRITICAL | Data Reliability Index: {health_score:.1f}% (Immediate intervention required)")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Processed Volume", f"{total_records:,}", "Rows ingested")
    col2.metric("Validated (Gold Data)", f"{total_clean:,}", f"{health_score:.1f}% compliance")
    col3.metric("Quarantined (Anomalies)", f"{total_quarantine:,}", f"{(100-health_score):.1f}% loss", delta_color="inverse")
    col4.metric("Active Constraints", "4 Rules", "Vectorized logic")

    st.markdown("<br>", unsafe_allow_html=True)

    tab_dash, tab_clean, tab_quarantine, tab_export = st.tabs([
        "Analytics Dashboard", 
        "Gold Data Layer", 
        "Quarantine Zone", 
        "Export Hub"
    ])

    with tab_dash:
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.markdown("#### Database Health Distribution")
            fig_health = px.pie(
                names=['Validated Data', 'Quarantined Data'],
                values=[total_clean, total_quarantine],
                hole=0.6,
                color_discrete_sequence=['#10b981', '#ef4444']
            )
            fig_health.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=380)
            st.plotly_chart(fig_health, use_container_width=True)

        with col_chart2:
            st.markdown("#### Governance: Top Rejection Reasons")
            if not df_quarantine.empty:
                df_reasons = df_quarantine['Rejection_Reason'].value_counts().reset_index()
                df_reasons.columns = ['Reason', 'Frequency']
                
                fig_bar = px.bar(
                    df_reasons, 
                    x='Frequency', 
                    y='Reason', 
                    orientation='h',
                    color='Frequency', 
                    color_continuous_scale='Reds',
                    text='Frequency'
                )
                fig_bar.update_layout(
                    margin=dict(t=20, b=20, l=20, r=20), 
                    height=380,
                    yaxis={'categoryorder':'total ascending'}
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("No anomalies detected in the current batch.")

    with tab_clean:
        st.markdown("#### Validated Corporate Data (Ready for BI/ML)")
        st.dataframe(df_clean, height=450, use_container_width=True)

    with tab_quarantine:
        st.markdown("#### Isolated Records (Dead-letter Queue)")
        st.dataframe(df_quarantine, height=450, use_container_width=True)

    with tab_export:
        st.markdown("#### Compliance & Backup Hub")
        st.write("Generate physical CSV artifacts for external audits or compliance reporting.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        b1, b2 = st.columns(2)
        
        if not df_clean.empty:
            csv_clean = df_clean.to_csv(index=False).encode('utf-8')
            b1.download_button("Download Gold Lote", data=csv_clean, file_name='validated_sales.csv', mime='text/csv', use_container_width=True)
            
        if not df_quarantine.empty:
            csv_corrupt = df_quarantine.to_csv(index=False).encode('utf-8')
            b2.download_button("Download Quarantine Matrix", data=csv_corrupt, file_name='quarantine_sales.csv', mime='text/csv', use_container_width=True)

if __name__ == "__main__":
    main()