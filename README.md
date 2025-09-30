# Vendor Performance Dashboard

A modern web application for analyzing vendor performance data with interactive charts and visualizations.

## Features

- **Secure Login System**: Username and password authentication
- **Dual Dashboard Interface**: PowerBI dashboard + custom analytics
- **PowerBI Integration**: Embedded PowerBI dashboard with full functionality
- **Interactive Custom Charts**: Real-time vendor performance analytics
- **Multiple Chart Types**: Bar charts, pie charts, scatter plots, and histograms
- **Responsive Design**: Works on desktop and mobile devices
- **Data Filtering**: Clean data analysis similar to the Jupyter notebook

## Login Credentials

- **Username**: `muniswaran`
- **Password**: `muniswaran@123`

## Installation & Setup

1. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the Server**:
   ```bash
   python app.py
   ```

3. **Access the Application**:
   Open your web browser and navigate to: `http://localhost:5000`

## Dashboard Features

### Summary Cards
- Total number of vendors
- Total sales amount
- Total profit
- Average profit margin

### Dashboard Interface

The application features a **dual-tab interface**:

#### Tab 1: PowerBI Dashboard
- **Embedded PowerBI Report**: Full-featured PowerBI dashboard with interactive visualizations
- **Real-time Data**: Connected to your PowerBI data source
- **Advanced Analytics**: Leverages PowerBI's powerful analytics capabilities

#### Tab 2: Custom Analytics
- **Top 10 Vendors by Sales**: Bar chart showing highest performing vendors
- **Top 10 Brands by Sales**: Bar chart showing best-selling brands
- **Vendor Purchase Contribution**: Doughnut chart showing purchase distribution
- **Bulk Purchase Analysis**: Bar chart analyzing order sizes
- **Profit Margin Distribution**: Histogram showing margin distribution
- **Sales vs Profit Margin**: Scatter plot showing correlation

### Data Table
- Detailed vendor performance data
- Sortable and filterable table
- First 50 records displayed

## Data Analysis

The dashboard includes analysis similar to the Jupyter notebook:

- **Vendor Performance Analysis**: Top and low performing vendors
- **Purchase Contribution**: Pareto analysis of vendor dependencies
- **Bulk Purchase Benefits**: Cost savings analysis by order size
- **Inventory Turnover**: Identification of slow-moving inventory
- **Profit Margin Analysis**: Statistical comparison between vendor groups

## Technical Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Charts**: Chart.js
- **Styling**: Bootstrap 5, Custom CSS
- **Data**: Pandas, SQLite
- **Authentication**: JWT-style token system

## File Structure

```
├── app.py                 # Flask backend server
├── index.html            # Main HTML page
├── script.js             # Frontend JavaScript
├── requirements.txt      # Python dependencies
├── vendor_sales_summary.csv  # Data source
└── README.md            # This file
```

## API Endpoints

- `POST /api/login` - User authentication
- `GET /api/vendor-data` - Get vendor performance data
- `GET /api/summary-stats` - Get summary statistics
- `GET /api/top-vendors` - Get top performing vendors
- `GET /api/top-brands` - Get top performing brands
- `GET /api/vendor-contribution` - Get vendor purchase contribution
- `GET /api/bulk-purchase-analysis` - Get bulk purchase analysis
- `GET /api/profit-margin-analysis` - Get profit margin analysis
- `GET /api/inventory-analysis` - Get inventory analysis

## Security Features

- Token-based authentication
- Protected API endpoints
- CORS configuration for secure requests

## Browser Compatibility

- Chrome (recommended)
- Firefox
- Safari
- Edge

## Troubleshooting

1. **Port Already in Use**: Change the port in `app.py` (line 211)
2. **Data Not Loading**: Ensure `vendor_sales_summary.csv` exists in the project directory
3. **Login Issues**: Verify credentials match exactly: `muniswaran` / `muniswaran@123`

## Development

To modify or extend the application:

1. **Backend Changes**: Edit `app.py` for API modifications
2. **Frontend Changes**: Edit `index.html` and `script.js` for UI changes
3. **Styling**: Modify CSS in `index.html` or add external stylesheets
4. **Charts**: Update Chart.js configurations in `script.js`
