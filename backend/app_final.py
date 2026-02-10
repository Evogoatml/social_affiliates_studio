from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Sample route
@app.route('/')
def home():
    return jsonify({'message': 'Welcome to the Flask app!'}), 200

@app.route('/api/influencers')
def get_influencers():
    influencers = [
        {'id': 1, 'name': 'Alice', 'niche': 'Fitness', 'followers': 120000},
        {'id': 2, 'name': 'Bob', 'niche': 'Fashion', 'followers': 80000},
        {'id': 3, 'name': 'Charlie', 'niche': 'Tech', 'followers': 200000},
    ]
    return jsonify(influencers), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)