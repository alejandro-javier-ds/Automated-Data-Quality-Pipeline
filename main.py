import time
import logging
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def get_sql_engine():
    conn_str = f"mssql+pyodbc://@{config.SERVER_NAME}/{config.DATABASE_NAME}?driver=ODBC+Driver+17+for+SQL+Server&Trusted_Connection=yes"
    return create_engine(conn_str, fast_executemany=True)

def extract_raw_data(engine):
    logging.info("Extracting data from Raw_Sales...")
    query = "SELECT * FROM Raw_Sales;"
    df = pd.read_sql(query, engine)
    logging.info(f"Extracted {len(df)} records.")
    return df

def audit_data(df):
    logging.info("Executing vectorized quality rules...")
    
    cond_null = df.isnull().any(axis=1) | (df['Product_Name'] == '')
    cond_qty = df['Quantity'] <= 0
    cond_price = df['Unit_Price'] < 0
    cond_email = ~df['Customer_Email'].astype(str).str.contains(r'^[\w\.-]+@[\w\.-]+\.\w+$', regex=True, na=False)

    conditions = [cond_null, cond_qty, cond_price, cond_email]
    choices = ['Missing/Null Values', 'Invalid Quantity', 'Invalid Price', 'Malformed Email']
    
    df['Rejection_Reason'] = np.select(conditions, choices, default=None)
    
    df_clean = df[df['Rejection_Reason'].isnull()].drop(columns=['Rejection_Reason']).copy()
    df_quarantine = df[df['Rejection_Reason'].notnull()].copy()
    
    logging.info(f"Quality Engine Results: {len(df_clean)} Clean | {len(df_quarantine)} Quarantined.")
    return df_clean, df_quarantine

def load_processed_data(engine, df_clean, df_quarantine):
    logging.info("Pushing processed data to destination tables...")
    
    with engine.connect() as conn:
        conn.execute(text("TRUNCATE TABLE Clean_Sales"))
        conn.execute(text("TRUNCATE TABLE Quarantine_Sales"))
        conn.commit()

    logging.info("Loading Clean_Sales...")
    df_clean.to_sql('Clean_Sales', con=engine, if_exists='append', index=False, chunksize=10000)
    
    logging.info("Loading Quarantine_Sales...")
    df_quarantine.to_sql('Quarantine_Sales', con=engine, if_exists='append', index=False, chunksize=10000)
    
    logging.info("Pipeline ETL Execution Completed.")

if __name__ == "__main__":
    start_time = time.time()
    
    try:
        engine = get_sql_engine()
        df_raw = extract_raw_data(engine)
        
        if not df_raw.empty:
            df_clean, df_quarantine = audit_data(df_raw)
            load_processed_data(engine, df_clean, df_quarantine)
            
        elapsed_time = round(time.time() - start_time, 2)
        logging.info(f"Total processing time: {elapsed_time} seconds.")
    except Exception as e:
        logging.error(f"Pipeline failed: {str(e)}")