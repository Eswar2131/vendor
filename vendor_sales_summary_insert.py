import pandas as pd
import sqlite3

# Connect to DB
conn = sqlite3.connect("vendor_data.db")

# Example DataFrame (replace with your real data)
vendor_sales_summary = pd.DataFrame({
    'VendorNumber': [101, 102],
    'VendorName': ['ABC Corp', 'XYZ Ltd'],
    'Brand': [1, 2]
    # add other columns...
})

# Now you can insert it
vendor_sales_summary.to_sql('vendor_sales_summary', conn, if_exists='append', index=False)

conn.commit()
conn.close()
