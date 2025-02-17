import pandas as pd
import psycopg2

# Database connection parameters
DB_CONFIG = {
    "dbname": "telecom",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": 5432
}

def load_data():
    """Connects to PostgreSQL and loads the xdr_data table into a DataFrame."""
    query = "SELECT * FROM public.xdr_data;"
    
    try:
        # Connect to the database
        conn = psycopg2.connect(**DB_CONFIG)
        df = pd.read_sql(query, conn)
        
        # Save raw data
        df.to_csv("data/raw/telecom_data.csv", index=False)
        print("Data successfully loaded and saved to data/raw/telecom_data.csv")
    
    except Exception as e:
        print(f"Error loading data: {e}")
    
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    load_data()
