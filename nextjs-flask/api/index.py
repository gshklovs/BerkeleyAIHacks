from flask import Flask, request
from models.assisted_merge import assistive_merge
from models.extract_nodes import extract_entities_and_relationships

app = Flask(__name__)


@app.route("/api/python")
def hello_world():
    return "<p>Hello, World!</p>"


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
