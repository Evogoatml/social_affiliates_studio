from flask import Flask, request, jsonify
import csv
from io import StringIO

app = Flask(__name__)

# Dummy data
influencers = []

# Create endpoint for POST /api/influencers
@app.route('/api/influencers', methods=['POST'])
def create_influencer():
    data = request.json
    influencer = {
        'id': len(influencers) + 1,
        'name': data['name'],
        'followers': data['followers'],
    }
    influencers.append(influencer)
    return jsonify(influencer), 201

# List endpoint for GET /api/influencers
@app.route('/api/influencers', methods=['GET'])
def list_influencers():
    search = request.args.get('search', '')
    filtered_influencers = [i for i in influencers if search.lower() in i['name'].lower()]
    return jsonify(filtered_influencers), 200

# Delete endpoint for DELETE /api/influencers/<id>
@app.route('/api/influencers/<int:id>', methods=['DELETE'])
def delete_influencer(id):
    global influencers
    influencers = [i for i in influencers if i['id'] != id]
    return '', 204

# Export CSV endpoint
@app.route('/api/influencers/export', methods=['GET'])
def export_influencers():
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Name', 'Followers'])
    for influencer in influencers:
        writer.writerow([influencer['id'], influencer['name'], influencer['followers']])
    response = app.response_class(
        response=output.getvalue(),
        status=200,
        mimetype='text/csv'
    )
    response.headers['Content-Disposition'] = 'attachment; filename=influencers.csv'
    return response

if __name__ == '__main__':
    app.run(debug=True)
