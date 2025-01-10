from flask import Flask, render_template, jsonify
from selenium_script import run_selenium_script
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__, template_folder="templates")  # Use 'templates' folder in src

# MongoDB connection
MONGODB_URI = os.getenv("MONGODB_URI")
client = MongoClient(MONGODB_URI)
db = client['TwitterTrends']
collection = db['TrendData']

@app.route("/")
def serve_html():
    return render_template("index.html")  # Render HTML from templates folder

@app.route("/run-script")
def run_script():
    try:
        # Run the Selenium script and insert data into MongoDB
        trend_data = run_selenium_script()

        # Get the latest record from MongoDB
        latest_record = collection.find_one({"_id": trend_data["_id"]})

        response = {
            "trends": [
                trend_data.get("trend1", "N/A"),
                trend_data.get("trend2", "N/A"),
                trend_data.get("trend3", "N/A"),
                trend_data.get("trend4", "N/A"),
                trend_data.get("trend5", "N/A"),
            ],
            "timestamp": trend_data["timestamp"],
            "ip_address": trend_data["ip_address"],
            "record": latest_record,
        }
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
