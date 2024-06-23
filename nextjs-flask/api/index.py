import asyncio
from flask import Flask, request, session
from flask_cors import CORS
from dotenv import dotenv_values
import random
from neo4j import GraphDatabase
from models.assisted_merge import assistive_merge
from models.extract_nodes import extract_entities_and_relationships
from models.speech_to_text import extract_text_from_audio
import json
import logging
from logging.handlers import RotatingFileHandler

config = dotenv_values(".env")
graphdb = GraphDatabase.driver(
    config["NEO4J_URI"], auth=(config["NEO4J_USER"], config["NEO4J_PASS"])
)
app = Flask(__name__)
CORS(app)

# Set the log level and format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Optionally, configure a rotating file handler
handler = RotatingFileHandler("app.log", maxBytes=10000, backupCount=1)
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
handler.setFormatter(formatter)
app.logger.addHandler(handler)

# define globals
prev_text = ""
global_entities = set()
global_relationships = []


@app.route("/api/python")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/api/upload_audio", methods=["POST"])
def upload_audio():
    audio_data = request.data
    with open("received_audio.wav", "ab") as audio_file:
        audio_file.write(audio_data)
    return "Audio received", 200


if __name__ == "__main__":
    # app.run(host='0.0.0.0', port=5328)
    pass


@app.route("/api/merge", methods=["POST"])  # needs work
def merge():
    data = request.get_json()
    paragraphs = data["paragraphs"]
    merged_text = assistive_merge(paragraphs)
    return merged_text


@app.route("/api/extract", methods=["POST"])  # needs work
def extract():
    data = request.get_json()
    merged_text = data["merged_text"]
    if "existing_entities" not in data:
        existing_entities = None
    else:
        existing_entities = data["existing_entities"]
    if "existing_relationships" not in data:
        existing_relationships = None
    else:
        existing_relationships = data["existing_relationships"]
    triplets = extract_entities_and_relationships(
        merged_text, existing_entities, existing_relationships
    )
    # triplets is returned as triplets, existing_entities, existing_relationships
    return triplets

@app.route("/api/current_path")
def current_path():
    result = graphdb.execute_query("MATCH p=(k)-[:RELATIONSHIP*1..]->(n:Entity {current: TRUE})-[:RELATIONSHIP*1..]->(m) return p order by length(p) DESC LIMIT 1")
    return [x["name"] for x in result[0][0]["p"].nodes]

@app.route("/api/create_node", methods=("POST",))
def create_node():
    data = request.get_json()
    graphdb.execute_query("MERGE (:Entity {name: $name})", name=data["entity"])
    return "DONE"


@app.route("/api/create_relationship", methods=("POST",))
def create_relationship():
    data = request.get_json()
    graphdb.execute_query(
        """
    MATCH (a:Entity {name: $source})
    MATCH (b:Entity {name: $dest})
    MERGE (a)-[:RELATIONSHIP {type: $relationship}]->(b)
    """,
        source=data["source"],
        dest=data["dest"],
        relationship=data["relationship"],
    )
    return "DONE"


@app.route("/api/create_relationships", methods=("POST",))
def create_relationships():
    data = request.get_json()
    with graphdb.session() as session:
        with session.begin_transaction() as tx:
            for entity in data["entities"]:
                tx.run("MERGE (:Entity {name: $name})", name=entity)
            for rel in data["relationships"]:
                tx.run(
                    """
                MATCH (a:Entity {name: $source})
                MATCH (b:Entity {name: $dest})
                MERGE (a)-[:RELATIONSHIP {type: $relationship}]->(b)
                """,
                    source=rel["source"],
                    dest=rel["dest"],
                    relationship=rel["relationship"],
                )
            tx.commit()
    return "DONE"




@app.route("/api/new_meeting")
def new_meeting():
    session["session_id"] = "".join(random.choices("ABCDEFGHJKMNPQRSTUVWXYZ"))
    return session["session_id"]


@app.route("/api/graph")
def graph():
    if not conn.is_connected():
        return "Not connected to database", 500
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT * FROM {config['SINGLESTORE_DB']} WHERE sessionId={session['session_id']}"
    )
    return cursor.fetchall()


@app.route("/api/speech_to_text", methods=["POST"])  # needs work
def speech_to_text():
    return extract_text_from_audio()

@app.route("/api/current_path")
def current_path():
    result = graphdb.execute_query("MATCH p=(k)-[:RELATIONSHIP*1..]->(n:Entity {current: TRUE})-[:RELATIONSHIP*1..]->(m) return p order by length(p) DESC LIMIT 1")
    return [x["name"] for x in result[0][0]["p"].nodes]

@app.route("/api/current_topic")
def current_topic():
    result = graphdb.execute_query("MATCH (n :Entity {current: TRUE}) RETURN n")
    return result[0][0]["n"]["name"]