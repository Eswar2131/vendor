from flask import Flask, request, jsonify, send_from_directory
import json
import os

# --- Basic Flask App Setup ---
app = Flask(__name__, static_folder='.')

# --- In-Memory Data Store ---
# In a real application, you would use a proper database.
# For this example, we'll load the JSON data into memory.
vendor_data = []
try:
    with open('vendor_sales_summary.json', 'r') as f:
        vendor_data = json.load(f)
except FileNotFoundError:
    print("\n--- WARNING ---")
    print("vendor_sales_summary.json not found. The chatbot will not have data context.")
    print("Please ensure the file exists and is in the correct directory.")


# --- API Endpoint for Chatbot ---
@app.route('/api/chat', methods=['POST'])
def chat_handler():
    """Handles chat messages by sending them to a mock AI model."""
    user_message = request.json.get('message', '').lower()

    if not user_message:
        return jsonify({'reply': "I'm sorry, I didn't receive a message."}), 400

    # --- Advanced AI Logic (Simulated) ---
    # In a real-world scenario, this is where you would call a powerful 
    # language model API (like OpenAI's GPT or Google's Gemini).
    # For this demonstration, we will simulate that with advanced logic.
    
    reply = get_ai_response(user_message)
    
    return jsonify({'reply': reply})


def get_ai_response(message):
    """Simulates an AI model providing intelligent responses about the data."""
    
    # Keyword-based analysis to simulate understanding
    if 'how many vendors' in message:
        num_vendors = len(set(v['VendorName'] for v in vendor_data))
        return f"There are {num_vendors} unique vendors in the dataset."

    if 'total sales' in message:
        total_sales = sum(v['TotalSalesDollars'] for v in vendor_data)
        return f"The total sales across all vendors is ${total_sales:,.2f}."

    if 'highest profit margin' in message:
        if not vendor_data:
            return "I don't have any data to analyze for profit margins."
        top_vendor = max(vendor_data, key=lambda v: v['ProfitMargin'])
        return f"The vendor with the highest profit margin is {top_vendor['VendorName']} with a margin of {top_vendor['ProfitMargin']:.2f}%."

    if 'top vendor by sales' in message:
        if not vendor_data:
            return "I can't determine the top vendor without sales data."
        vendor_sales = {}
        for v in vendor_data:
            vendor_sales[v['VendorName']] = vendor_sales.get(v['VendorName'], 0) + v['TotalSalesDollars']
        top_vendor_name = max(vendor_sales, key=vendor_sales.get)
        return f"The top vendor by sales is {top_vendor_name} with ${vendor_sales[top_vendor_name]:,.2f} in sales."

    # Default response if no specific keywords are matched
    return "I am a sophisticated AI, but I am still in training. I can answer questions about the number of vendors, total sales, and vendors with the highest profit margins."


# --- Static File Serving ---
# This will serve your main HTML, CSS, and JS files
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)


# --- Main Execution ---
if __name__ == '__main__':
    print("\n--- Vendor Performance Dashboard Server ---")
    print("Starting server on http://127.0.0.1:5000")
    print("To stop the server, press CTRL+C")
    app.run(port=5000, debug=True)
