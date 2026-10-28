import json
from flask import Flask, render_template, jsonify
import os

app = Flask(__name__)

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
TRACES_PATH = os.path.join(DATA_DIR, 'traces.jsonl')
METRICS_PATH = os.path.join(DATA_DIR, 'metrics.json')

def load_latest_trace():
    if not os.path.exists(TRACES_PATH):
        return None
    with open(TRACES_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        if not lines:
            return None
        # take last line (most recent)
        return json.loads(lines[-1])

def load_metrics():
    if not os.path.exists(METRICS_PATH):
        return {}
    with open(METRICS_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

@app.route('/')
def index():
    trace = load_latest_trace()
    metrics = load_metrics()
    return render_template('index.html', trace=trace, metrics=metrics)

@app.route('/api/trace')
def api_trace():
    return jsonify(load_latest_trace() or {})

@app.route('/api/metrics')
def api_metrics():
    return jsonify(load_metrics())

if __name__ == '__main__':
    # Run on host port 5000
    app.run(host='0.0.0.0', port=5000, debug=False)
