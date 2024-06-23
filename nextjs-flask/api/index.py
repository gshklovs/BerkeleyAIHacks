from flask import Flask, request, session
from flask_cors import CORS
from dotenv import dotenv_values
import random
from neo4j import GraphDatabase
from models.assisted_merge import assistive_merge
from models.extract_nodes import extract_entities_and_relationships

config = dotenv_values(".env")
graphdb = GraphDatabase.driver(config["NEO4J_URI"], auth=(config["NEO4J_USER"], config["NEO4J_PASS"]))
app = Flask(__name__)
CORS(app)

@app.route("/api/python")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route('/api/upload_audio', methods=['POST'])
def upload_audio():
    audio_data = request.data
    with open("received_audio.wav", "ab") as audio_file:
        audio_file.write(audio_data)
    return 'Audio received', 200

if __name__ == '__main__':
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
    #triplets is returned as triplets, existing_entities, existing_relationships
    return triplets

def create_node(entity):
    graphdb.execute_query("CREATE (:Entity {name: $name})", name=entity)

@app.route("/api/create_node", methods=("POST",))
def create_node_req():
    data = request.get_json()
    graphdb.execute_query("CREATE (:Entity {name: $name})", name=data["entity"])
    return "DONE"

@app.route("/api/create_relationship", methods=("POST",))
def create_relationship():
    data = request.get_json()
    graphdb.execute_query("""
    MATCH (a:Entity {name: $source})
    MATCH (b:Entity {name: $dest})
    MERGE (a)-[:RELATIONSHIP {type: $relationship}]->(b)
    """, source=data["source"], dest=data["dest"], relationship=data["relationship"])
    return "DONE"

@app.route("/api/create_relationships", methods=("POST",))
def create_relationships():
    data = request.get_json()
    with graphdb.session() as session:
        with session.begin_transaction() as tx:
            for entity in data["entities"]:
                tx.run("CREATE (:Entity {name: $name})", name=entity)
            for rel in data["relationships"]:
                tx.run("""
                MATCH (a:Entity {name: $source})
                MATCH (b:Entity {name: $dest})
                MERGE (a)-[:RELATIONSHIP {type: $relationship}]->(b)
                """, source=rel["source"], dest=rel["dest"], relationship=rel["relationship"])
            tx.commit()
    return "DONE"

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
