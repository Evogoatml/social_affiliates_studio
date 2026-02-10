from flask import Flask, jsonify

app = Flask(__name__)

# Sample route
@app.route('/')
def home():
    return jsonify({'message': 'Welcome to the Flask app!'}), 200

if __name__ == '__main__':
    app.run(debug=True)
