from flask import Flask
from models.assited_merge import assistive_merge
from models.extract_nodes import extract_entities_and_relationships

app = Flask(__name__)


@app.route("/api/python")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/api/merge", methods=["POST"])  # needs work
def merge():
    paragraphs = request.json["paragraphs"]
    merged_text = assistive_merge(paragraphs)
    return merged_text


@app.route("/api/extract", methods=["POST"])  # needs work
def extract():
    merged_text = request.json["merged_text"]
    existing_entities = request.json["existing_entities"]
    existing_relationships = request.json["existing_relationships"]
    triplets = extract_entities_and_relationships(
        merged_text, existing_entities, existing_relationships
    )
    return triplets
