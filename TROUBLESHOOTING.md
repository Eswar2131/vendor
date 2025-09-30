# Troubleshooting Guide

## Login Page Works but Dashboard Not Loading

If you can log in successfully but the dashboard isn't loading properly, follow these steps:

### Step 1: Check Browser Console
1. Open the web application in your browser
2. Press `F12` or right-click and select "Inspect Element"
3. Go to the "Console" tab
4. Look for any error messages (they will be in red)
5. Try logging in again and watch the console for messages

### Step 2: Check Network Tab
1. In the developer tools, go to the "Network" tab
2. Try logging in again
3. Look for any failed requests (they will be in red)
4. Check if the `/api/vendor-data` request returns data

### Step 3: Common Issues and Solutions

#### Issue: "Failed to fetch" or Network Error
**Solution**: Make sure the Flask server is running
```bash
python app.py
```
You should see:
```
Starting Vendor Performance Dashboard Server...
Access the application at: http://localhost:5000
```

#### Issue: "Unauthorized" or 401 Error
**Solution**: Make sure you're using the correct credentials:
- Username: `muniswaran`
- Password: `muniswaran@123`

#### Issue: Charts Not Displaying
**Solution**: Check if Chart.js is loading properly
1. In the Console tab, type: `Chart`
2. If it shows "undefined", there's a Chart.js loading issue
3. Try refreshing the page

#### Issue: Data Not Loading
**Solution**: Check if the CSV file exists
1. Make sure `vendor_sales_summary.csv` is in the same directory as `app.py`
2. Check if the file has data (should be around 10,000+ rows)

### Step 4: Manual Testing

#### Test the API directly:
1. Open a new browser tab
2. Go to: `http://localhost:5000/api/vendor-data`
3. You should see JSON data (if not logged in, you'll get an error)
4. This confirms the backend is working

#### Test with curl (if available):
```bash
curl -H "Authorization: Bearer authenticated_user" http://localhost:5000/api/vendor-data
```

### Step 5: Reset and Restart

If nothing works:
1. Stop the Flask server (Ctrl+C)
2. Restart it: `python app.py`
3. Clear your browser cache (Ctrl+Shift+Delete)
4. Try again

### Step 6: Check File Permissions

Make sure all files are readable:
- `index.html`
- `script.js`
- `app.py`
- `vendor_sales_summary.csv`

### Expected Console Output

When working correctly, you should see in the console:
```
Vendor data loaded: [number] records
Updating summary cards with [number] records
Summary stats: {totalVendors: [number], totalSales: [number], ...}
```

### Still Having Issues?

If you're still experiencing problems:
1. Check the terminal where Flask is running for error messages
2. Make sure you have all dependencies installed: `pip install Flask Flask-CORS pandas numpy`
3. Try a different browser (Chrome, Firefox, Edge)
4. Check if your firewall is blocking localhost:5000
