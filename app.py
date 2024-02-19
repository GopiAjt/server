from flask import Flask, request, jsonify, g
from flask_cors import CORS
import json
from datetime import datetime
import sqlite3

app = Flask(__name__)
CORS(app)

# SQLite database file path
sqlite_db_path = 'flask_test.db'

# Connect to SQLite within each request
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('contacts.db')
    return db

# Create a table if it doesn't exist
def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS Contact (
            id INTEGER PRIMARY KEY,
            phoneNumber TEXT,
            email TEXT,
            linkedId INTEGER,
            linkPrecedence TEXT,
            createdAt DATETIME,
            updatedAt DATETIME,
            deletedAt DATETIME
        );
        '''
        cursor.execute(create_table_query)
        db.commit()

# Endpoint for identifying and consolidating contacts
@app.route('/identify', methods=['POST'])
def identify_contact():
    data = request.json
    email = data.get('email')
    phone_number = data.get('phoneNumber')

    if email is None and phone_number is None:
        return jsonify({"error": "Either email or phoneNumber must be provided"}), 400

    conn = get_db()
    cursor = conn.cursor()

    # Check if contact already exists
    cursor.execute('SELECT * FROM Contact WHERE email=? OR phoneNumber=?', (email, phone_number))
    existing_contact = cursor.fetchone()

    if existing_contact:
        # Get the column names from the cursor description
        column_names = [description[0] for description in cursor.description]
    
    # Zip the column names with the fetched data to create a dictionary
        existing_contact = dict(zip(column_names, existing_contact))
        # If contact exists, update its information
        primary_contact_id = existing_contact['id']
        cursor.execute('UPDATE Contact SET updatedAt=? WHERE id=?', (datetime.now(), primary_contact_id))
    else:
        # If contact does not exist, create a new primary contact
        cursor.execute('INSERT INTO Contact (email, phoneNumber, linkedId, linkPrecedence, createdAt, updatedAt) VALUES (?, ?, ?, ?, ?, ?)',
                       (email, phone_number, None, "primary", datetime.now(), datetime.now()))
        primary_contact_id = cursor.lastrowid

    # Check for secondary contacts
    if existing_contact:
        # If contact already exists, create a secondary contact
        secondary_contact_id = cursor.lastrowid
        cursor.execute('INSERT INTO Contact (email, phoneNumber, linkedId, linkPrecedence, createdAt, updatedAt) VALUES (?, ?, ?, ?, ?, ?)',
                       (email, phone_number, primary_contact_id, "secondary", datetime.now(), datetime.now()))
        secondary_contact_id = cursor.lastrowid
    else:
        secondary_contact_id = None

    conn.commit()
    conn.close()

   # Get consolidated contact details
    consolidated_contact = {
    "primaryContatctId": primary_contact_id,
    "emails": [existing_contact['email'], email] if existing_contact and existing_contact['email'] else [email],
    "phoneNumbers": [existing_contact['phoneNumber']] if existing_contact and existing_contact['phoneNumber'] else [phone_number],
    "secondaryContactIds": [secondary_contact_id] if secondary_contact_id else []
    }

    return jsonify({"contact": consolidated_contact}), 200

@app.route('/get', methods=['GET'])
def getData():
    return jsonify('HELLO')

if __name__ == '__main__':
    init_db()  # Initialize the database
    app.run(debug=True)
