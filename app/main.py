from flask import Flask, request, jsonify
from database import init_db, save_word_pair, get_db_connection
import os

app = Flask(__name__)

# Initialize database on startup
with app.app_context():
    init_db()

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200

@app.route('/api/mirror', methods=['GET'])
def mirror():
    word = request.args.get('word', '')
    
    if not word:
        return jsonify({"error": "word parameter is required"}), 400
    
    # Transform: swap case
    swapped = word.swapcase()
    
    # Reverse the string
    transformed = swapped[::-1]
    
    # Save to database
    save_word_pair(word, transformed)
    
    return jsonify({"transformed": transformed}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4004, debug=False)