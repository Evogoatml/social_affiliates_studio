from flask import Flask, jsonify, request

app = Flask(__name__)

# In-memory store for accounts
accounts = []

@app.route('/accounts', methods=['GET'])
def get_accounts():
    return jsonify(accounts)

@app.route('/accounts', methods=['POST'])
def add_account():
    account_data = request.json
    accounts.append(account_data)
    return jsonify(account_data), 201

@app.route('/accounts/<int:account_id>', methods=['GET'])
def get_account(account_id):
    account = next((acc for acc in accounts if acc.get('id') == account_id), None)
    if account:
        return jsonify(account)
    return jsonify({'error': 'Account not found'}), 404

@app.route('/accounts/<int:account_id>', methods=['PUT'])
def update_account(account_id):
    account_data = request.json
    account = next((acc for acc in accounts if acc.get('id') == account_id), None)
    if account:
        account.update(account_data)
        return jsonify(account)
    return jsonify({'error': 'Account not found'}), 404

@app.route('/accounts/<int:account_id>', methods=['DELETE'])
def delete_account(account_id):
    global accounts
    accounts = [acc for acc in accounts if acc.get('id') != account_id]
    return jsonify({'result': 'Account deleted'})

if __name__ == '__main__':
    app.run(debug=True)