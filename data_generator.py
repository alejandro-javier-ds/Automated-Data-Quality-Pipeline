import random
import time
import logging
import pandas as pd
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

def generate_synthetic_data(num_records: int = 100000) -> pd.DataFrame:
    products = ['Laptop HP ProBook', 'Logitech MX Master', 'Dell UltraSharp Monitor', 'Razer BlackWidow', 'USB-C Hub']
    domains = ['gmail.com', 'hotmail.com', 'enterprise.com', 'outlook.com']
    
    data = []
    
    for i in range(1, num_records + 1):
        is_corrupt = random.random() < 0.15
        
        product = random.choice(products)
        quantity = random.randint(1, 10)
        price = round(random.uniform(20.0, 1500.0), 2)
        email = f"client_{i}@{random.choice(domains)}"
        
        if is_corrupt:
            error_type = random.choice(['negative_qty', 'negative_price', 'bad_email', 'null_product'])
            
            if error_type == 'negative_qty':
                quantity = random.randint(-10, -1)
            elif error_type == 'negative_price':
                price = round(random.uniform(-500.0, -1.0), 2)
            elif error_type == 'bad_email':
                email = f"client_{i}_NO_DOMAIN.com"
            elif error_type == 'null_product':
                product = None
                
        data.append({
            'Transaction_ID': i,
            'Product_Name': product,
            'Quantity': quantity,
            'Unit_Price': price,
            'Customer_Email': email,
            'Transaction_Date': pd.Timestamp.now() - pd.Timedelta(days=random.randint(0, 365))
        })
        
    return pd.DataFrame(data)

def load_to_staging(df: pd.DataFrame):
    engine = get_sql_engine()
    
    with engine.connect() as conn:
        conn.execute(text("TRUNCATE TABLE Raw_Sales"))
        conn.commit()
    
    df.to_sql('Raw_Sales', con=engine, if_exists='append', index=False, chunksize=10000)

if __name__ == "__main__":
    start_time = time.time()
    
    logging.info("Generating 100,000 synthetic records in memory...")
    df_raw = generate_synthetic_data(100000)
    
    logging.info("Pushing data to SQL Server (Raw_Sales)...")
    load_to_staging(df_raw)
    
    elapsed_time = round(time.time() - start_time, 2)
    logging.info(f"Pipeline finished successfully in {elapsed_time} seconds.")