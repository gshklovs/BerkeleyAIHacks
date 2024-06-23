import asyncio
from flask import Flask, request, session
from flask_cors import CORS
from dotenv import dotenv_values
import random
from neo4j import GraphDatabase
from models.assisted_merge import assistive_merge
from models.extract_nodes import extract_entities_and_relationships
from models.speech_to_text import extract_text_from_audio
from models.similarities import compute_similarities
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


# async def websocket_handler(websocket, path):
#     async for message in websocket:
#         audio_data = message
#         with open("received_audio.wav", "ab") as audio_file:
#             audio_file.write(audio_data)

#         text_segment = extract_text_from_audio("received_audio.wav")
#         if 'previous_text' in session:
#             merged_text = assistive_merge([session['previous_text'], text_segment])
#         else:
#             merged_text = text_segment

#         session['previous_text'] = merged_text

#         triplets, existing_entities, existing_relationships = extract_entities_and_relationships(
#             merged_text, existing_entities, existing_relationships
#         )

#         with graphdb.session() as db_session:
#             with db_session.begin_transaction() as tx:
#                 for entity in existing_entities:
#                     tx.run("MERGE (:Entity {name: $name})", name=entity)
#                 for src, rel, dest in existing_relationships:
#                     tx.run("""
#                     MATCH (a:Entity {name: $source})
#                     MATCH (b:Entity {name: $dest})
#                     MERGE (a)-[:RELATIONSHIP {type: $relationship}]->(b)
#                     """, source=src, dest=dest, relationship=rel)
#                 tx.commit()

#         await websocket.send(json.dumps({'entities': list(existing_entities), 'relationships': existing_relationships}))


@app.route("/api/record_and_build", methods=["POST"])
def record_and_build():
    global prev_text, global_entities, global_relationships

    audio_file = request.files["file"]
    audio_file.save("received_audio.mp3")
    app.logger.info("Audio file saved")

    text_segment = extract_text_from_audio("received_audio.mp3")
    app.logger.info(f"Extracted text: {text_segment}")
    if prev_text:
        merged_text = assistive_merge([prev_text, text_segment])
    else:
        merged_text = text_segment
    app.logger.info(f"Merged text: {merged_text}")
    prev_text = merged_text

    prev_entities = global_entities.copy()
    app.logger.info(f"Previous entities: {prev_entities}")
    prev_relationships = global_relationships.copy()
    app.logger.info(f"Previous relationships: {prev_relationships}")
    mode = "Build"
    triplets, global_entities, global_relationships = (
        extract_entities_and_relationships(
            merged_text, mode, global_entities, global_relationships
        )
    )

    remaining_entities = set(global_entities) - set(prev_entities)
    remaining_relationships = set(global_relationships) - set(prev_relationships)

    with graphdb.session() as db_session:
        with db_session.begin_transaction() as tx:
            for entity in remaining_entities:
                tx.run("MERGE (:Entity {name: $name})", name=entity)
            for src, rel, dest in remaining_relationships:
                tx.run(
                    """
                MATCH (a:Entity {name: $source})
                MATCH (b:Entity {name: $dest})
                MERGE (a)-[:RELATIONSHIP {type: $relationship}]->(b)
                """,
                    source=src,
                    dest=dest,
                    relationship=rel,
                )
            tx.commit()
    app.logger.info("Entities and relationships created in database")
    return "DONE"


@app.route("/api/create_correlation_edges", methods=["POST"])
def create_correlation_edges():
    global global_entities
    
    # Compute similarities
    similarities = compute_similarities(global_entities)
    threshold = 0.7  # You can adjust this threshold as needed
    
    correlation_edges = [
        (entity1, entity2) for (entity1, entity2), sim in similarities.items() if sim > threshold
    ]
    
    with graphdb.session() as db_session:
        with db_session.begin_transaction() as tx:
            for src, dest in correlation_edges:
                tx.run(
                    """
                    MATCH (a:Entity {name: $source})
                    MATCH (b:Entity {name: $dest})
                    MERGE (a)-[:CORRELATED {similarity: $similarity}]->(b)
                    """,
                    source=src,
                    dest=dest,
                    similarity=similarities[(src, dest)],
                )
            tx.commit()
    app.logger.info("Correlation edges created in database")
    return "DONE"



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5328)
