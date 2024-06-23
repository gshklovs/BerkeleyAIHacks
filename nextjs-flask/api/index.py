from flask import Flask, request, session
from dotenv import dotenv_values
import random
from neo4j import GraphDatabase

config = dotenv_values(".env")
graphdb = GraphDatabase.driver(config["NEO4J_URI"], auth=(config["NEO4J_USER"], config["NEO4J_PASS"]))
app = Flask(__name__)



@app.route("/api/python")
def hello_world():
    return f"<p>Asdf</p>"

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

