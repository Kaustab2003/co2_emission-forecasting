from flask import Flask, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

DATA_FILE = 'api_emission_data.json'
API_USERS_FILE = 'api_users.json'
API_LOG_FILE = 'api_log.json'

# Helper to load/save data
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_api_users():
    if not os.path.exists(API_USERS_FILE):
        return {}
    with open(API_USERS_FILE, 'r') as f:
        return json.load(f)

def log_update(username, company, emission_sources):
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'username': username,
        'company': company,
        'emission_sources': emission_sources
    }
    if os.path.exists(API_LOG_FILE):
        with open(API_LOG_FILE, 'r') as f:
            logs = json.load(f)
    else:
        logs = []
    logs.append(log_entry)
    with open(API_LOG_FILE, 'w') as f:
        json.dump(logs, f, indent=2)

def validate_emission_sources(emission_sources):
    if not isinstance(emission_sources, list):
        return False, 'emission_sources must be a list.'
    for idx, src in enumerate(emission_sources):
        if not isinstance(src, dict):
            return False, f'Emission source at index {idx} is not a dict.'
        if "type" not in src or "emission" not in src:
            return False, f'Missing required fields in emission source at index {idx}.'
        if not isinstance(src["emission"], (int, float)):
            return False, f'Emission value at index {idx} is not a number.'
        if src["emission"] < 0:
            return False, f'Negative emission value at index {idx}.'
    return True, None

@app.route('/update_emissions', methods=['POST'])
def update_emissions():
    req = request.get_json()
    if not req:
        return jsonify({'error': 'Missing JSON body'}), 400
    username = req.get('username')
    api_key = req.get('api_key')
    company = req.get('company')
    emission_sources = req.get('emission_sources')
    if not username or not api_key or not company or not emission_sources:
        return jsonify({'error': 'Missing username, api_key, company, or emission_sources'}), 400
    api_users = load_api_users()
    if username not in api_users or api_users[username] != api_key:
        return jsonify({'error': 'Invalid API key for user'}), 403
    # Data validation
    valid, err = validate_emission_sources(emission_sources)
    if not valid:
        return jsonify({'error': f'Invalid emission_sources: {err}'}), 400
    data = load_data()
    data[company] = emission_sources
    save_data(data)
    log_update(username, company, emission_sources)
    return jsonify({'status': 'success', 'company': company, 'emission_sources': emission_sources})

@app.route('/get_emissions', methods=['GET'])
def get_emissions():
    username = request.args.get('username')
    api_key = request.args.get('api_key')
    company = request.args.get('company')
    if not username or not api_key or not company:
        return jsonify({'error': 'Missing username, api_key, or company'}), 400
    api_users = load_api_users()
    if username not in api_users or api_users[username] != api_key:
        return jsonify({'error': 'Invalid API key for user'}), 403
    data = load_data()
    if company not in data:
        return jsonify({'error': 'Company not found'}), 404
    return jsonify({'company': company, 'emission_sources': data[company]})

if __name__ == '__main__':
    app.run(port=5001, debug=True) 