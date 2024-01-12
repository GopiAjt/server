from flask import Flask, request, jsonify, g
from flask_cors import CORS
import json
import sqlite3

app = Flask(__name__)
CORS(app)

# SQLite database file path
sqlite_db_path = 'flask_test.db'

# Connect to SQLite within each request
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(sqlite_db_path)
    return db

# Create a table if it doesn't exist
def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            phone_no TEXT
        );
        '''
        cursor.execute(create_table_query)
        db.commit()

@app.route('/post', methods=['POST'])
def postData():
    data = request.get_json()

    # Insert data into the SQLite database
    query = "INSERT INTO user (name, age, phone_no) VALUES (?, ?, ?)"
    values = (data['name'], data['age'], data['phone_no'])

    db = get_db()
    cursor = db.cursor()
    cursor.execute(query, values)
    db.commit()

    return 'uploaded!'

@app.route('/get', methods=['GET'])
def getData():
    # Retrieve data from the SQLite database
    query = "SELECT * FROM user"

    db = get_db()
    cursor = db.cursor()
    cursor.execute(query)
    data = cursor.fetchall()

    # Convert the nested array structure to an array of JSON objects
    json_data = []
    for row in data:
        json_data.append({
            'id': row[0],
            'name': row[1],
            'age': row[2],
            'phone_no': row[3]
        })

    return jsonify(json_data)

if __name__ == '__main__':
    init_db()  # Initialize the database
    app.run(debug=True)
