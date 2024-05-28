from flask import Flask, render_template, jsonify
import logging
from datetime import datetime
import random

app = Flask(__name__)

# Dummy logger for demonstration purposes
class Logger:
    def report_data(self, value, sensor_name):
        print(f"{sensor_name}: {value}")

logger = Logger()
data_list = []

@app.route('/')
def home():
    return render_template('display_data.html')

@app.route('/get_data', methods=['GET'])
def get_data():
    data = random.uniform(20.0, 30.0)  # Simulating sensor data
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logger.report_data(data, "Sensor")
    data_list.append({"timestamp": timestamp, "data": data})
    if len(data_list) > 10:
        data_list.pop(0)  # Keep only the last 10 entries
    return jsonify(data_list)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
