from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pandas as pd
import sqlite3
import os
from functools import wraps
import json

app = Flask(__name__)
CORS(app)

# Configuration
VALID_USERNAME = "muniswaran"
VALID_PASSWORD = "muniswaran@123"

# Authentication decorator
def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid authorization header'}), 401
        
        token = auth_header.split(' ')[1]
        if token != "authenticated_user":
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

# Load vendor data
def load_vendor_data():
    """Load vendor data from CSV file"""
    try:
        if os.path.exists('vendor_sales_summary.csv'):
            df = pd.read_csv('vendor_sales_summary.csv')
            # Filter data similar to the Jupyter notebook
            df = df[(df['GrossProfit'] > 0) & 
                   (df['ProfitMargin'] > 0) & 
                   (df['TotalSalesQuantity'] > 0)]


            return df.to_dict('records')
        else:
            return []
    except Exception as e:
        print(f"Error loading vendor data: {e}")
        return []

# Routes
@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    """Serve static files"""
    return send_from_directory('.', filename)

@app.route('/api/login', methods=['POST'])
def login():
    """Handle user login"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if username == VALID_USERNAME and password == VALID_PASSWORD:
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'token': 'authenticated_user'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Invalid username or password'
            }), 401
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Login failed'
        }), 500

@app.route('/api/vendor-data')
@require_auth
def get_vendor_data():
    """Get vendor performance data"""
    try:
        data = load_vendor_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': 'Failed to load vendor data'}), 500

@app.route('/api/summary-stats')
@require_auth
def get_summary_stats():
    """Get summary statistics"""
    try:
        data = load_vendor_data()
        if not data:
            return jsonify({'error': 'No data available'}), 404
        
        df = pd.DataFrame(data)
        
        stats = {
            'totalVendors': df['VendorName'].nunique(),
            'totalSales': float(df['TotalSalesDollars'].sum()),
            'totalProfit': float(df['GrossProfit'].sum()),
            'avgMargin': float(df['ProfitMargin'].mean()),
            'totalPurchaseDollars': float(df['TotalPurchaseDollars'].sum()),
            'totalSalesQuantity': float(df['TotalSalesQuantity'].sum()),
            'avgStockTurnover': float(df['StockTurnover'].mean())
        }
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': 'Failed to calculate summary statistics'}), 500

@app.route('/api/top-vendors')
@require_auth
def get_top_vendors():
    """Get top performing vendors"""
    try:
        data = load_vendor_data()
        if not data:
            return jsonify({'error': 'No data available'}), 404
        
        df = pd.DataFrame(data)
        top_vendors = df.groupby('VendorName')['TotalSalesDollars'].sum().nlargest(10)
        
        result = []
        for vendor, sales in top_vendors.items():
            vendor_data = df[df['VendorName'] == vendor].iloc[0]
            result.append({
                'vendorName': vendor,
                'totalSales': float(sales),
                'totalProfit': float(df[df['VendorName'] == vendor]['GrossProfit'].sum()),
                'avgMargin': float(df[df['VendorName'] == vendor]['ProfitMargin'].mean()),
                'totalPurchaseDollars': float(df[df['VendorName'] == vendor]['TotalPurchaseDollars'].sum())
            })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': 'Failed to get top vendors'}), 500

@app.route('/api/top-brands')
@require_auth
def get_top_brands():
    """Get top performing brands"""
    try:
        data = load_vendor_data()
        if not data:
            return jsonify({'error': 'No data available'}), 404
        
        df = pd.DataFrame(data)
        top_brands = df.groupby('Description')['TotalSalesDollars'].sum().nlargest(10)
        
        result = []
        for brand, sales in top_brands.items():
            result.append({
                'brandName': brand,
                'totalSales': float(sales),
                'totalProfit': float(df[df['Description'] == brand]['GrossProfit'].sum()),
                'avgMargin': float(df[df['Description'] == brand]['ProfitMargin'].mean())
            })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': 'Failed to get top brands'}), 500

@app.route('/api/vendor-contribution')
@require_auth
def get_vendor_contribution():
    """Get vendor purchase contribution data"""
    try:
        data = load_vendor_data()
        if not data:
            return jsonify({'error': 'No data available'}), 404
        
        df = pd.DataFrame(data)
        vendor_contribution = df.groupby('VendorName')['TotalPurchaseDollars'].sum().nlargest(10)
        total_purchases = df['TotalPurchaseDollars'].sum()
        
        result = []
        cumulative = 0
        for vendor, purchase in vendor_contribution.items():
            contribution_pct = (purchase / total_purchases) * 100
            cumulative += contribution_pct
            result.append({
                'vendorName': vendor,
                'purchaseDollars': float(purchase),
                'contributionPct': float(contribution_pct),
                'cumulativePct': float(cumulative)
            })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': 'Failed to get vendor contribution'}), 500

@app.route('/api/bulk-purchase-analysis')
@require_auth
def get_bulk_purchase_analysis():
    """Get bulk purchase analysis data"""
    try:
        data = load_vendor_data()
        if not data:
            return jsonify({'error': 'No data available'}), 404
        
        df = pd.DataFrame(data)
        
        # Calculate unit purchase price
        df['UnitPurchasePrice'] = df['TotalPurchaseDollars'] / df['TotalPurchaseQuantity']
        
        # Create order size categories
        df['OrderSize'] = pd.qcut(df['TotalPurchaseQuantity'], q=3, labels=["Small", "Medium", "Large"])
        
        # Analyze by order size
        bulk_analysis = df.groupby('OrderSize').agg({
            'UnitPurchasePrice': 'mean',
            'TotalPurchaseQuantity': 'count'
        }).reset_index()
        
        result = []
        for _, row in bulk_analysis.iterrows():
            result.append({
                'orderSize': row['OrderSize'],
                'avgUnitPrice': float(row['UnitPurchasePrice']),
                'orderCount': int(row['TotalPurchaseQuantity'])
            })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': 'Failed to get bulk purchase analysis'}), 500

@app.route('/api/profit-margin-analysis')
@require_auth
def get_profit_margin_analysis():
    """Get profit margin analysis data"""
    try:
        data = load_vendor_data()
        if not data:
            return jsonify({'error': 'No data available'}), 404
        
        df = pd.DataFrame(data)
        
        # Define top and low performing vendors
        top_threshold = df['TotalSalesDollars'].quantile(0.75)
        low_threshold = df['TotalSalesDollars'].quantile(0.25)
        
        top_vendors = df[df['TotalSalesDollars'] >= top_threshold]['ProfitMargin']
        low_vendors = df[df['TotalSalesDollars'] <= low_threshold]['ProfitMargin']
        
        result = {
            'topVendors': {
                'mean': float(top_vendors.mean()),
                'std': float(top_vendors.std()),
                'count': len(top_vendors)
            },
            'lowVendors': {
                'mean': float(low_vendors.mean()),
                'std': float(low_vendors.std()),
                'count': len(low_vendors)
            },
            'allVendors': {
                'mean': float(df['ProfitMargin'].mean()),
                'std': float(df['ProfitMargin'].std()),
                'count': len(df)
            }
        }
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': 'Failed to get profit margin analysis'}), 500

@app.route('/api/inventory-analysis')
@require_auth
def get_inventory_analysis():
    """Get inventory turnover and unsold inventory analysis"""
    try:
        data = load_vendor_data()
        if not data:
            return jsonify({'error': 'No data available'}), 404
        
        df = pd.DataFrame(data)
        
        # Calculate unsold inventory value
        df['UnsoldInventoryValue'] = (df['TotalPurchaseQuantity'] - df['TotalSalesQuantity']) * df['PurchasePrice']
        
        # Low turnover vendors
        low_turnover = df[df['StockTurnover'] < 1].groupby('VendorName')['StockTurnover'].mean().nsmallest(10)
        
        # Top vendors with locked capital
        inventory_value = df.groupby('VendorName')['UnsoldInventoryValue'].sum().nlargest(10)
        
        result = {
            'totalUnsoldCapital': float(df['UnsoldInventoryValue'].sum()),
            'lowTurnoverVendors': [
                {
                    'vendorName': vendor,
                    'avgStockTurnover': float(turnover)
                }
                for vendor, turnover in low_turnover.items()
            ],
            'topLockedCapitalVendors': [
                {
                    'vendorName': vendor,
                    'lockedCapital': float(capital)
                }
                for vendor, capital in inventory_value.items()
            ]
        }
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': 'Failed to get inventory analysis'}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("Starting Vendor Performance Dashboard Server...")
    print("Access the application at: http://localhost:5000")
    print("Login credentials:")
    print(f"Username: {VALID_USERNAME}")
    print(f"Password: {VALID_PASSWORD}")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
