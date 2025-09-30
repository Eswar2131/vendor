import pandas as pd
import sqlite3
import os

DB_FILE = 'inventory.db'
OUTPUT_FILE = 'vendor_sales_summary.json'

# --- Main script logic ---
def main():
    """Connects to the database, extracts cleaned data, and saves it to JSON."""
    
    print(f"Attempting to connect to database: {DB_FILE}...")
    
    if not os.path.exists(DB_FILE):
        print(f"\n--- ERROR ---")
        print(f"Database file '{DB_FILE}' not found.")
        print("Please make sure you are in the correct directory and the database file exists.")
        return

    try:
        conn = sqlite3.connect(DB_FILE)
        
        # This query replicates the final data cleaning step from the notebook
        query = """
        SELECT * 
        FROM vendor_sales_summary
        WHERE GrossProfit > 0 AND ProfitMargin > 0
        """
        
        print("Executing query to get cleaned vendor data...")
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if df.empty:
            print("\n--- WARNING ---")
            print("The query returned no data. The output JSON file will be empty.")
        else:
            print(f"Successfully fetched {len(df)} records.")

        # Save the DataFrame to the JSON file required by the dashboard
        df.to_json(OUTPUT_FILE, orient='records')
        
        print(f"\n--- SUCCESS ---")
        print(f"Successfully created '{OUTPUT_FILE}'.")
        print("You can now return to the chat and tell me the file has been created.")

    except Exception as e:
        print(f"\n--- ERROR ---")
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()
