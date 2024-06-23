from flask import Flask, request, session
from dotenv import dotenv_values
import random
import singlestoredb as s2
import atexit
app = Flask(__name__)

config = dotenv_values(".env")
conn = s2.connect(
    host=config["SINGLESTORE_HOST"],
    port=config["SINGLESTORE_PORT"],
    user=config["SINGLESTORE_USER"],
    password=config["SINGLESTORE_PASSWD"],
    database=config["SINGLESTORE_DB"],
    connect_timeout=5)

def close_connections():
    conn.close()

atexit.register(close_connections)

@app.route("/api/python")
def hello_world():
    return f"<p>Asdf</p>"

@app.route("/api/add_relationships", methods=("POST",))
def add_relationships():
    if not conn.is_connected():
        return "Not connected to database", 500
    if request.method == "POST":
        data = request.get_json()
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO {config['SINGLESTORE_DB']} VALUES ({data['srcEntity']}, {data['relationship']}, {data['destEntity']}, {session['session_id']});")
        return "DONE"
    return "Need a POST request to add data", 405

@app.route("/api/new_meeting")
def new_meeting():
    session["session_id"] = ''.join(random.choices("ABCDEFGHJKMNPQRSTUVWXYZ"))
    return session["session_id"]

@app.route("/api/graph")
def graph():
    if not conn.is_connected():
        return "Not connected to database", 500
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {config['SINGLESTORE_DB']} WHERE sessionId={session['session_id']}")
    return cursor.fetchall()

@app.route("/api/existing_entities")
def 
