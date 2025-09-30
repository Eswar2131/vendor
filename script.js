// Global variables
let vendorData = [];
let charts = {};
let authToken = null;

document.addEventListener('DOMContentLoaded', () => {
    // This ensures the DOM is fully loaded before we attach listeners
    const loginForm = document.getElementById('loginForm');
    if(loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
});

// --- Login and Page Navigation ---
async function handleLogin(e) {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    // Simplified login for local demonstration
    if (username === "muniswaran" && password === "muniswaran@123") {
        authToken = 'fake-jwt-token'; 
        showDashboard();
        loadDashboardData();
    } else {
        showLoginError();
    }
}

function showLoginError() {
    const loginError = document.getElementById('loginError');
    loginError.style.display = 'block';
    setTimeout(() => {
        loginError.style.display = 'none';
    }, 3000);
}

function showDashboard() {
    document.getElementById('loginHeader').style.display = 'none';
    document.getElementById('loginPage').style.display = 'none';
    document.getElementById('dashboardPage').style.display = 'block';
    document.getElementById('chatbotContainer').style.display = 'block';
}

function logout() {
    document.getElementById('dashboardPage').style.display = 'none';
    document.getElementById('loginHeader').style.display = 'block';
    document.getElementById('loginPage').style.display = 'flex';
    document.getElementById('chatbotContainer').style.display = 'none';

    authToken = null;
    vendorData = [];
    Object.values(charts).forEach(chart => {
        if (chart && typeof chart.destroy === 'function') chart.destroy();
    });
    charts = {};
    
    document.getElementById('loginForm').reset();
    showSection('home');
}

// --- Main Dashboard Logic ---
async function loadDashboardData() {
    document.getElementById('loading').style.display = 'block';
    document.getElementById('mainDashboardContent').style.display = 'none';
    document.getElementById('errorContainer').style.display = 'none';

    try {
        updateLoadingStatus('Fetching vendor data...');
        
        const response = await fetch('vendor_sales_summary.json'); 
        if (!response.ok) {
            throw new Error(`Failed to load data file: ${response.statusText}`);
        }
        vendorData = await response.json();

        updateLoadingStatus('Populating dashboard...');
        updateSummaryCards();
        createAllCharts();
        
        updateLoadingStatus('Dashboard ready!');
        setTimeout(() => {
            document.getElementById('loading').style.display = 'none';
            document.getElementById('mainDashboardContent').style.display = 'block';
        }, 500);

    } catch (error) {
        console.error('Error loading dashboard data:', error);
        document.getElementById('loading').style.display = 'none';
        const errorContainer = document.getElementById('errorContainer');
        errorContainer.innerHTML = `<div class="alert alert-danger"><strong>Error:</strong> ${error.message}. Please refresh the page.</div>`;
        errorContainer.style.display = 'block';
    }
}

function updateLoadingStatus(message) {
    document.getElementById('loadingStatus').innerHTML += `<div class="text-success">✓ ${message}</div>`;
}

function updateSummaryCards() {
    const totalVendors = new Set(vendorData.map(v => v.VendorName)).size;
    const totalSales = vendorData.reduce((sum, v) => sum + v.TotalSalesDollars, 0);
    const totalProfit = vendorData.reduce((sum, v) => sum + v.GrossProfit, 0);
    const avgMargin = vendorData.length > 0 ? vendorData.reduce((sum, v) => sum + v.ProfitMargin, 0) / vendorData.length : 0;

    document.getElementById('totalVendors').textContent = totalVendors.toLocaleString();
    document.getElementById('totalSales').textContent = formatCurrency(totalSales);
    document.getElementById('totalProfit').textContent = formatCurrency(totalProfit);
    document.getElementById('avgMargin').textContent = avgMargin.toFixed(1) + '%';
}


// --- Chart Creation ---
function createAllCharts() {
    createTopVendorsChart();
    createTopBrandsChart();
    createVendorContributionChart();
    createBulkPurchaseChart();
    createSalesVsMarginChart();
    createProfitMarginChart();
    createConfidenceIntervalChart();
}

function createTopVendorsChart() {
    const vendorSales = vendorData.reduce((acc, item) => {
        acc[item.VendorName] = (acc[item.VendorName] || 0) + item.TotalSalesDollars;
        return acc;
    }, {});
    const topVendors = Object.entries(vendorSales).sort(([, a], [, b]) => b - a).slice(0, 10);

    const ctx = document.getElementById('topVendorsChart').getContext('2d');
    if (charts.topVendors) charts.topVendors.destroy();
    charts.topVendors = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: topVendors.map(([name]) => name.substring(0, 15)),
            datasets: [{
                label: 'Sales ($)',
                data: topVendors.map(([, sales]) => sales),
                backgroundColor: 'rgba(102, 126, 234, 0.8)',
            }]
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { callback: value => formatCurrency(value) } } } }
    });
}

function createTopBrandsChart() {
    const brandSales = vendorData.reduce((acc, item) => {
        acc[item.Description] = (acc[item.Description] || 0) + item.TotalSalesDollars;
        return acc;
    }, {});
    const topBrands = Object.entries(brandSales).sort(([, a], [, b]) => b - a).slice(0, 10);

    const ctx = document.getElementById('topBrandsChart').getContext('2d');
    if (charts.topBrands) charts.topBrands.destroy();
    charts.topBrands = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: topBrands.map(([name]) => name.substring(0, 20)),
            datasets: [{
                label: 'Sales ($)',
                data: topBrands.map(([, sales]) => sales),
                backgroundColor: 'rgba(118, 75, 162, 0.8)',
            }]
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { callback: value => formatCurrency(value) } } } }
    });
}

function createVendorContributionChart() {
    const vendorPurchases = vendorData.reduce((acc, item) => {
        acc[item.VendorName] = (acc[item.VendorName] || 0) + item.TotalPurchaseDollars;
        return acc;
    }, {});
    const topVendors = Object.entries(vendorPurchases).sort(([, a], [, b]) => b - a).slice(0, 10);
    const totalPurchases = Object.values(vendorPurchases).reduce((sum, val) => sum + val, 0);
    const otherVendors = totalPurchases - topVendors.reduce((sum, [, val]) => sum + val, 0);

    const ctx = document.getElementById('vendorContributionChart').getContext('2d');
    if (charts.vendorContribution) charts.vendorContribution.destroy();
    charts.vendorContribution = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: [...topVendors.map(([name]) => name), 'Other Vendors'],
            datasets: [{
                data: [...topVendors.map(([, val]) => val), otherVendors],
                backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40', '#C9CBCF']
            }]
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom' } } }
    });
}

function createBulkPurchaseChart() {
    const quantities = vendorData.map(v => v.TotalPurchaseQuantity).sort((a, b) => a - b);
    const q1 = quantities[Math.floor(quantities.length / 3)];
    const q2 = quantities[Math.floor(quantities.length * 2 / 3)];
    const orderSizes = { 'Small': 0, 'Medium': 0, 'Large': 0 };
    vendorData.forEach(item => {
        if (item.TotalPurchaseQuantity <= q1) orderSizes.Small++;
        else if (item.TotalPurchaseQuantity <= q2) orderSizes.Medium++;
        else orderSizes.Large++;
    });

    const ctx = document.getElementById('bulkPurchaseChart').getContext('2d');
    if (charts.bulkPurchase) charts.bulkPurchase.destroy();
    charts.bulkPurchase = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(orderSizes),
            datasets: [{
                label: 'Number of Orders',
                data: Object.values(orderSizes),
                backgroundColor: ['rgba(255, 99, 132, 0.8)', 'rgba(54, 162, 235, 0.8)', 'rgba(255, 206, 86, 0.8)']
            }]
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } }
    });
}

function createSalesVsMarginChart() {
    const scatterData = vendorData.map(v => ({ x: v.TotalSalesDollars, y: v.ProfitMargin }));
    
    const ctx = document.getElementById('salesVsMarginChart').getContext('2d');
    if (charts.salesVsMargin) charts.salesVsMargin.destroy();
    charts.salesVsMargin = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Sales vs Profit Margin',
                data: scatterData,
                backgroundColor: 'rgba(153, 102, 255, 0.6)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { type: 'logarithmic', title: { display: true, text: 'Total Sales ($) - Log Scale' }, ticks: { callback: value => formatCurrency(value) } },
                y: { title: { display: true, text: 'Profit Margin (%)' } }
            }
        }
    });
}

function createProfitMarginChart() {
    const margins = vendorData.map(v => v.ProfitMargin);
    const binCount = 20;
    const minMargin = Math.min(...margins);
    const maxMargin = Math.max(...margins);
    const binSize = (maxMargin - minMargin) / binCount;
    
    const bins = new Array(binCount).fill(0);
    const labels = new Array(binCount).fill(0).map((_, i) => (minMargin + i * binSize).toFixed(1));

    margins.forEach(margin => {
        const binIndex = Math.floor((margin - minMargin) / binSize);
        if(binIndex < binCount) bins[binIndex]++;
    });

    const ctx = document.getElementById('profitMarginChart').getContext('2d');
    if (charts.profitMargin) charts.profitMargin.destroy();
    charts.profitMargin = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Frequency',
                data: bins,
                backgroundColor: 'rgba(75, 192, 192, 0.6)',
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { title: { display: true, text: 'Profit Margin (%)' } },
                y: { title: { display: true, text: 'Frequency' }, beginAtZero: true }
            }
        }
    });
}

function createConfidenceIntervalChart() {
    const topVendorsData = vendorData.filter(v => v.TotalSalesDollars > vendorData.map(v => v.TotalSalesDollars).reduce((a, b) => a + b, 0) * 0.05);
    const lowVendorsData = vendorData.filter(v => v.TotalSalesDollars < vendorData.map(v => v.TotalSalesDollars).reduce((a, b) => a + b, 0) * 0.01);

    const topMargins = topVendorsData.map(v => v.ProfitMargin);
    const lowMargins = lowVendorsData.map(v => v.ProfitMargin);

    const ctx = document.getElementById('confidenceIntervalChart').getContext('2d');
    if (charts.confidenceInterval) charts.confidenceInterval.destroy();
    charts.confidenceInterval = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Top Vendors', 'Low Vendors'],
            datasets: [{
                label: 'Average Profit Margin',
                data: [
                    topMargins.reduce((a, b) => a + b, 0) / topMargins.length,
                    lowMargins.reduce((a, b) => a + b, 0) / lowMargins.length
                ],
                backgroundColor: ['rgba(54, 162, 235, 0.6)', 'rgba(255, 99, 132, 0.6)'],
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { title: { display: true, text: 'Average Profit Margin (%)' }, beginAtZero: true }
            }
        }
    });
}


// --- Helper & Navigation Functions ---
function formatCurrency(value) {
    if (Math.abs(value) >= 1000000) return '$' + (value / 1000000).toFixed(1) + 'M';
    if (Math.abs(value) >= 1000) return '$' + (value / 1000).toFixed(1) + 'K';
    return '$' + value.toFixed(0);
}

function showSection(sectionId, event) {
    if (event) event.preventDefault();
    document.getElementById('mainDashboardContent').style.display = 'none';
    document.getElementById('infoSections').style.display = 'none';
    document.querySelectorAll('.main-nav .nav-link').forEach(link => link.classList.remove('active'));

    if (sectionId === 'home') {
        document.getElementById('mainDashboardContent').style.display = 'block';
    } else {
        const infoContainer = document.getElementById('infoSections');
        let content = '';
        if (sectionId === 'about') content = getAboutContent();
        else if (sectionId === 'services') content = getServicesContent();
        else if (sectionId === 'contact') content = getContactContent();
        infoContainer.innerHTML = content;
        infoContainer.style.display = 'block';
    }
    if (event) event.currentTarget.classList.add('active');
}

function showHomeContent(event) { 
    showSection('home', event); 
}

function getAboutContent() {
    return `
        <div class="card card-custom animate__animated animate__fadeIn">
            <div class="card-header text-center">
                <h3><i class="fas fa-info-circle me-2"></i>About Vendor Performance Analytics</h3>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-6">
                        <h5><i class="fas fa-chart-line me-2 text-primary"></i>Our Mission</h5>
                        <p>We provide comprehensive analytics solutions to help businesses optimize their vendor relationships and maximize profitability through data-driven insights.</p>
                        
                        <h5><i class="fas fa-target me-2 text-success"></i>Our Vision</h5>
                        <p>To become the leading platform for vendor performance management, enabling businesses to make informed decisions and achieve sustainable growth.</p>
                    </div>
                    <div class="col-md-6">
                        <h5><i class="fas fa-users me-2 text-info"></i>Our Team</h5>
                        <p>Our team consists of experienced data scientists, business analysts, and software engineers dedicated to delivering cutting-edge analytics solutions.</p>
                        
                        <h5><i class="fas fa-award me-2 text-warning"></i>Our Values</h5>
                        <p>Innovation, integrity, and excellence drive everything we do. We believe in empowering businesses with actionable insights.</p>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function getServicesContent() {
    return `
        <div class="card card-custom animate__animated animate__fadeIn">
            <div class="card-header text-center">
                <h3><i class="fas fa-cogs me-2"></i>Our Comprehensive Services</h3>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-4 mb-4 text-center">
                        <div class="logo-icon mx-auto mb-3"><i class="fas fa-chart-bar"></i></div>
                        <h5>Interactive Dashboard</h5>
                        <p>Gain real-time insights with our dynamic and customizable analytics dashboard, tracking KPIs like sales, profit margins, and stock turnover.</p>
                    </div>
                    <div class="col-md-4 mb-4 text-center">
                        <div class="logo-icon mx-auto mb-3"><i class="fas fa-database"></i></div>
                        <h5>Advanced Data Management</h5>
                        <p>We provide secure, scalable data storage and processing solutions, ensuring data integrity and enabling powerful reporting capabilities.</p>
                    </div>
                    <div class="col-md-4 mb-4 text-center">
                        <div class="logo-icon mx-auto mb-3"><i class="fas fa-file-alt"></i></div>
                        <h5>Custom Reporting</h5>
                        <p>Generate bespoke reports tailored to your specific business needs, allowing you to focus on the metrics that matter most to your organization.</p>
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-4 mb-4 text-center">
                        <div class="logo-icon mx-auto mb-3"><i class="fas fa-brain"></i></div>
                        <h5>Predictive Analytics</h5>
                        <p>Leverage machine learning models to forecast future vendor performance, identify potential supply chain risks, and make proactive decisions.</p>
                    </div>
                    <div class="col-md-4 mb-4 text-center">
                        <div class="logo-icon mx-auto mb-3"><i class="fas fa-mobile-alt"></i></div>
                        <h5>Full Mobile Access</h5>
                        <p>Access your complete analytics suite from anywhere in the world with our fully responsive and feature-rich mobile-friendly platform.</p>
                    </div>
                    <div class="col-md-4 mb-4 text-center">
                        <div class="logo-icon mx-auto mb-3"><i class="fas fa-headset"></i></div>
                        <h5>Dedicated 24/7 Support</h5>
                        <p>Our expert support team is available around the clock to assist with any technical issues and provide training for optimal platform usage.</p>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function getContactContent() {
    return `
        <div class="card card-custom animate__animated animate__fadeIn">
            <div class="card-header text-center">
                <h3><i class="fas fa-envelope me-2"></i>Contact Us</h3>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-6">
                        <h5><i class="fas fa-map-marker-alt me-2 text-primary"></i>Address</h5>
                        <p>Kumaeasamy Layout<br>Banashankari<br>Bangalore, Karnataka</p>
                        
                        <h5><i class="fas fa-phone me-2 text-success"></i>Phone</h5>
                        <p>+91 8925369336</p>
                        
                        <h5><i class="fas fa-envelope me-2 text-info"></i>Email</h5>
                        <p>muniswaran@gmail.com</p>
                    </div>
                    <div class="col-md-6">
                        <form>
                            <div class="mb-3">
                                <label class="form-label">Name</label>
                                <input type="text" class="form-control" placeholder="Your Name">
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Email</label>
                                <input type="email" class="form-control" placeholder="your@email.com">
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Message</label>
                                <textarea class="form-control" rows="4" placeholder="Your message"></textarea>
                            </div>
                            <button type="submit" class="btn btn-custom w-100">
                                <i class="fas fa-paper-plane me-2"></i>Send Message
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// --- Chatbot ---
function toggleChatbot() { document.getElementById('chatbotWindow').style.display = document.getElementById('chatbotWindow').style.display === 'none' ? 'flex' : 'none'; }
function handleChatbotKeyPress(event) { if (event.key === 'Enter') sendChatbotMessage(); }
function sendChatbotMessage() {
    const input = document.getElementById('chatbotInput');
    const message = input.value.trim();
    if (message === '') return;
    addMessage(message, 'user');
    input.value = '';
    setTimeout(() => { addMessage(generateBotResponse(message), 'bot'); }, 500);
}
function addMessage(text, sender) {
    const messagesContainer = document.getElementById('chatbotMessages');
    const messageElement = document.createElement('div');
    messageElement.className = `message ${sender}`;
    messageElement.innerHTML = `<div class="message-content">${text}</div>`;
    messagesContainer.appendChild(messageElement);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}
function generateBotResponse(message) {
    message = message.toLowerCase();
    if (message.includes('sales')) return `Total sales are ${formatCurrency(vendorData.reduce((sum, v) => sum + v.TotalSalesDollars, 0))}.`;
    if (message.includes('profit')) return `Total profit is ${formatCurrency(vendorData.reduce((sum, v) => sum + v.GrossProfit, 0))}.`;
    return "I can answer questions about sales and profit. What would you like to know?";
}
