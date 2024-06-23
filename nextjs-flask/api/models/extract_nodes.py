import os
from llama_index.llms.groq import Groq
from llama_index.core.llms import ChatMessage
from llama_index.graph_stores.nebula import NebulaGraphStore
from llama_index.core import StorageContext
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import KnowledgeGraphRAGRetriever
from dotenv import dotenv_values

config = dotenv_values(".env")

llm = Groq(model="llama3-70b-8192", api_key=config["GROQ_API_KEY"])


def extract_entities_and_relationships(
    merged_text, existing_entities=None, existing_relationships=None
):
    """
    Extracts entities and relationships from the given text, considering existing entities and relationships
    to avoid redundancy. This function utilizes the Groq LLM for the extraction process.

    Args:
    - merged_text (str): The text from which to extract entities and relationships.
    - existing_entities (set): The set of existing entities.
    - existing_relationships (list): The list of existing relationships.

    Returns:
    - list: A list of new entity-relationship triplets.
    """
    if existing_entities is None:
        existing_entities = set()
    if existing_relationships is None:
        existing_relationships = []
    current_entities = "\n".join(existing_entities)
    current_relationships = "\n".join(
        f"{r[0]} - {r[1]} - {r[2]}" for r in existing_relationships
    )

    response = llm.chat(
        messages=[
            ChatMessage(role="system", content="You are a helpful assistant."),
            ChatMessage(
                role="user",
                content=(
                    "Extract detailed entities and relationships without excessive redundancy from the following text:\n"
                    f"{merged_text}\n"
                    "Current entities:\n" + current_entities + "\n"
                    "Current relationships:\n" + current_relationships + "\n"
                    "BE DETAILED INITIALLY, THEN COMPARE TO CURRENT RELATIONSHIPS AND SEE IF FIT TO ADD NEW ONE\n"
                    "DO NOT HAVE DUPLICATES\n"
                    "Please provide the output strictly in the following format with no variance:\n"
                    "1. Source Entity: <source entity>\n"
                    "2. Relationship: <relationship>\n"
                    "3. Destination Entity: <destination entity>\n"
                    "Ensure that each triplet is listed in the exact same format for consistency and avoid redundancy."
                    "\nExamples:\n"
                    "1. Source Entity: alice\n2. Relationship: is the CEO of\n3. Destination Entity: acme corp\n"
                    "1. Source Entity: acme corp\n2. Relationship: will acquire\n3. Destination Entity: widget inc\n"
                    "1. Source Entity: bob\n2. Relationship: is the CTO of\n3. Destination Entity: acme corp\n"
                    "1. Source Entity: john\n2. Relationship: works at\n3. Destination Entity: google\n"
                    "1. Source Entity: sarah\n2. Relationship: is married to\n3. Destination Entity: david\n"
                    "1. Source Entity: amazon\n2. Relationship: acquired\n3. Destination Entity: whole foods\n"
                    "1. Source Entity: elon musk\n2. Relationship: founded\n3. Destination Entity: spacex\n"
                    "1. Source Entity: jane\n2. Relationship: lives in\n3. Destination Entity: new york\n"
                    "1. Source Entity: microsoft\n2. Relationship: developed\n3. Destination Entity: windows\n"
                    "1. Source Entity: professor smith\n2. Relationship: teaches\n3. Destination Entity: mathematics\n"
                    "1. Source Entity: tesla\n2. Relationship: launched\n3. Destination Entity: model s\n"
                    "1. Source Entity: facebook\n2. Relationship: rebranded to\n3. Destination Entity: meta\n"
                    "1. Source Entity: bill gates\n2. Relationship: co-founded\n3. Destination Entity: microsoft\n"
                    "1. Source Entity: jon\n2. Relationship: is married to\n3. Destination Entity: sara\n"
                    "OUTPUT MODEL IN THIS FORMAT AND DETAIL\n"
                ),
            ),
        ]
    )
    structured_response = response.message.content.strip()
    triplets = parse_entities_and_relationships(structured_response)
    triplets, existing_entities, existing_relationships = (
        update_entities_and_relationships(
            triplets, existing_entities, existing_relationships
        )
    )
    return triplets, existing_entities, existing_relationships


def parse_entities_and_relationships(structured_response):
    """
    Parses the structured response to extract entity-relationship triplets.

    Args:
    - structured_response (str): The structured response containing entity-relationship data.

    Returns:
    - list: A list of dictionaries representing the triplets.
    """
    lines = structured_response.split("\n")
    triplets = []
    current_triplet = {}

    for line in lines:
        if line.startswith("1. Source Entity:"):
            if current_triplet:
                triplets.append(current_triplet)
                current_triplet = {}
            current_triplet["source"] = normalize_entity_name(
                line.replace("1. Source Entity:", "").strip()
            )
        elif line.startswith("2. Relationship:"):
            current_triplet["relationship"] = line.replace(
                "2. Relationship:", ""
            ).strip()
        elif line.startswith("3. Destination Entity:"):
            current_triplet["destination"] = normalize_entity_name(
                line.replace("3. Destination Entity:", "").strip()
            )

    if current_triplet:
        triplets.append(current_triplet)

    return triplets


def normalize_entity_name(entity):
    """
    Normalizes the entity name for consistency.

    Args:
    - entity (str): The entity name to normalize.

    Returns:
    - str: The normalized entity name.
    """
    entity = entity.lower().strip()
    entity = entity.replace("inc.", "inc").replace("corp.", "corp")
    return entity


def update_entities_and_relationships(
    triplets, existing_entities=None, existing_relationships=None
):
    """
    Updates the global sets of entities and relationships with new triplets.

    Args:
    - triplets (list): A list of dictionaries representing the triplets.
    """
    for triplet in triplets:
        try:
            source = normalize_entity_name(triplet["source"])
            destination = normalize_entity_name(triplet["destination"])

            if source not in existing_entities:
                existing_entities.add(source)
            if destination not in existing_entities:
                existing_entities.add(destination)

            relationship = (source, triplet["relationship"], destination)
            if relationship not in existing_relationships:
                existing_relationships.append(relationship)
        except KeyError as e:
            print(f"Missing key in triplet: {e}")
    return triplets, existing_entities, existing_relationships
