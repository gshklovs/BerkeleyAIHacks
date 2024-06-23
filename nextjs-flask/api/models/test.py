from assisted_merge import assistive_merge
from extract_nodes import extract_entities_and_relationships
from transformers import BertModel, BertTokenizer
import torch.nn.functional as F
import torch

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')
#paragraphs
paragraphs = [
    "The team encountered high latency due to a large dataset, which was solved by upgrading the server.",
    "Slow response time was addressed by optimizing the query execution.",
    "Low accuracy in the model was improved by gathering more diverse data.",
    "Network issues were frequent, and the solution was to check the connection regularly.",
    "Data inconsistency problems were solved by implementing a robust data validation process.",
    "A recent security breach was addressed by enhancing security measures and conducting regular audits.",
    "Poor performance was identified to be due to inefficient code, which was optimized to improve speed.",
    "The software faced numerous bugs, and debugging helped in stabilizing the application.",
    "System crashes were frequent because of outdated software, which was updated to the latest version.",
    "User complaints about the interface were resolved by providing thorough user training and updating the user guide."
]

# Initialize existing entities and relationships
prev_text = ""
existing_entities = set()
existing_relationships = []

def get_entity_embedding(entity):
    inputs = tokenizer(entity, return_tensors='pt')
    with torch.no_grad():
        outputs = model(**inputs)
    embeddings = outputs.last_hidden_state.mean(dim=1).squeeze()
    return embeddings

def cosine_similarity(embedding1, embedding2):
    cos_sim = F.cosine_similarity(embedding1.unsqueeze(0), embedding2.unsqueeze(0))
    return cos_sim.item()

def compute_similarities(entities):
    embeddings = {entity: get_entity_embedding(entity) for entity in entities}
    similarities = {}
    
    for i, entity1 in enumerate(entities):
        for j, entity2 in enumerate(entities):
            if i < j:  # Avoid redundant computations
                sim = cosine_similarity(embeddings[entity1], embeddings[entity2])
                similarities[(entity1, entity2)] = sim
                
    return similarities

def evaluate_extraction(paragraphs):
    global existing_entities, existing_relationships, prev_text
    for paragraph in paragraphs:
        if prev_text != "":
            merged_text = assistive_merge([prev_text, paragraph])
        else:
            merged_text = paragraph

        prev_text = paragraph

        prev_entities = existing_entities.copy()
        prev_relationships = existing_relationships.copy()
        mode = "Build"
        triplets, existing_entities, existing_relationships = extract_entities_and_relationships(
            merged_text, mode, existing_entities, existing_relationships
        )

        remaining_entities = set(existing_entities) - set(prev_entities)
        remaining_relationships = set(existing_relationships) - set(prev_relationships)

        # print("Paragraph:", paragraph)
        # print("Extracted Entities:", remaining_entities)
        # print("Extracted Relationships:", remaining_relationships)
        # print()
    
    print("Final Entities:", existing_entities)
    print("Final Relationships:", existing_relationships)

    similarities = compute_similarities(list(existing_entities))
    for pair, sim in similarities.items():
        if sim > .85:
            print(f"Similarity between {pair[0]} and {pair[1]}: {sim}")


# Run evaluation
evaluate_extraction(paragraphs)


