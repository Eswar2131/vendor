import os
import sqlite3
import pandas as pd
import logging
import random
from datetime import datetime, timedelta

# ================================
# CONFIGURATION
# ================================
CSV_FOLDER = "data"  # folder where your CSV files are stored
CSV_FILES = {
    "purchases": "purchases.csv",
    "vendor_invoice": "vendor_invoice.csv",
    "purchase_prices": "purchase_prices.csv",
    "sales": "sales.csv"
}
DB_FILE = "inventory.db"

# Ensure logs folder exists
os.makedirs("logs", exist_ok=True)

# Logging setup — logs to file + console
logging.basicConfig(
    filename="logs/get_vendor_summary.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="a"
)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logging.getLogger().addHandler(console_handler)


def load_csv_to_db(conn):
    """Load required CSV files into the SQLite database."""
    for table_name, file_name in CSV_FILES.items():
        file_path = os.path.join(CSV_FOLDER, file_name)
        if not os.path.exists(file_path):
            logging.error(f"Missing CSV file: {file_path}")
            raise FileNotFoundError(f"Required CSV not found: {file_path}")
        
        logging.info(f"Loading {file_name} into table '{table_name}'...")
        df = pd.read_csv(file_path)
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        logging.info(f"Loaded {len(df)} rows into '{table_name}'.")


def ingest_db(df, table_name, engine):
    """Ingest the dataframe into a database table."""
    df.to_sql(table_name, con=engine, if_exists='replace', index=False)


def create_vendor_summary(conn):
    """Merge different tables to get vendor summary and add new columns."""
    query = """
    WITH FreightSummary AS (
        SELECT VendorNumber, SUM(Freight) AS FreightCost
        FROM vendor_invoice
        GROUP BY VendorNumber
    ), 
    PurchaseSummary AS (
        SELECT p.VendorNumber, p.VendorName, p.Brand, p.Description, p.PurchasePrice,
               pp.Price AS ActualPrice, pp.Volume,
               SUM(p.Quantity) AS TotalPurchaseQuantity,
               SUM(p.Dollars) AS TotalPurchaseDollars
        FROM purchases p
        JOIN purchase_prices pp ON p.Brand = pp.Brand
        WHERE p.PurchasePrice > 0
        GROUP BY p.VendorNumber, p.VendorName, p.Brand, p.Description,
                 p.PurchasePrice, pp.Price, pp.Volume
    ), 
    SalesSummary AS (
        SELECT VendorNo, Brand,
               SUM(SalesQuantity) AS TotalSalesQuantity,
               SUM(SalesDollars) AS TotalSalesDollars,
               SUM(SalesPrice) AS TotalSalesPrice,
               SUM(ExciseTax) AS TotalExciseTax
        FROM sales
        GROUP BY VendorNo, Brand
    ) 
    SELECT ps.VendorNumber, ps.VendorName, ps.Brand, ps.Description,
           ps.PurchasePrice, ps.ActualPrice, ps.Volume,
           ps.TotalPurchaseQuantity, ps.TotalPurchaseDollars,
           ss.TotalSalesQuantity, ss.TotalSalesDollars, ss.TotalSalesPrice,
           ss.TotalExciseTax, fs.FreightCost
    FROM PurchaseSummary ps
    LEFT JOIN SalesSummary ss 
        ON ps.VendorNumber = ss.VendorNo AND ps.Brand = ss.Brand
    LEFT JOIN FreightSummary fs 
        ON ps.VendorNumber = fs.VendorNumber
    ORDER BY ps.TotalPurchaseDollars DESC
    """
    return pd.read_sql_query(query, conn)


def clean_data(df):
    """Clean and enhance data for analysis."""
    df['Volume'] = df['Volume'].astype(float)
    df.fillna(0, inplace=True)
    df['VendorName'] = df['VendorName'].str.strip()
    df['Description'] = df['Description'].str.strip()

    df['GrossProfit'] = df['TotalSalesDollars'] - df['TotalPurchaseDollars']
    df['ProfitMargin'] = (df['GrossProfit'] / df['TotalSalesDollars']) * 100
    df['StockTurnover'] = df['TotalSalesQuantity'] / df['TotalPurchaseQuantity']
    df['SalesToPurchaseRatio'] = df['TotalSalesDollars'] / df['TotalPurchaseDollars']

    return df


if __name__ == '__main__':
    conn = None
    try:
        # Connect to DB
        conn = sqlite3.connect(DB_FILE)

        # Step 1: Load CSVs into DB
        load_csv_to_db(conn)

        # Step 2: Create summary
        logging.info('Creating Vendor Summary Table...')
        summary_df = create_vendor_summary(conn)
        logging.info(f"Summary shape: {summary_df.shape}")
        logging.debug(summary_df.head().to_string())

        # Step 3: Clean data
        logging.info('Cleaning Data...')
        clean_df = clean_data(summary_df)
        logging.info(f"Cleaned Data shape: {clean_df.shape}")
        logging.debug(clean_df.head().to_string())

        # Step 4: Save final table
        logging.info('Ingesting Data...')
        ingest_db(clean_df, 'vendor_sales_summary', conn)

        # Step 5: Add Date Column and Export to CSV
        output_csv = "vendor_sales_summary.csv"

        # Add simulated date column
        if 'Date' not in clean_df.columns:
            start_date = datetime.now() - timedelta(days=365)
            end_date = datetime.now()
            clean_df['Date'] = [start_date + timedelta(seconds=random.randint(0, int((end_date - start_date).total_seconds()))) for _ in range(len(clean_df))]
            clean_df['Date'] = pd.to_datetime(clean_df['Date']).dt.date

        clean_df.to_csv(output_csv, index=False)
        logging.info(f"Exported vendor summary to {output_csv}")

        logging.info('Process Completed Successfully.')

    except Exception as e:
        logging.error(f"Error occurred: {e}", exc_info=True)

    finally:
        if conn:
            conn.close()
            logging.info('Database connection closed.')
