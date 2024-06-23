from assisted_merge import assistive_merge
from extract_nodes import extract_entities_and_relationships
from transformers import BertModel, BertTokenizer
import torch.nn.functional as F
import torch

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')
#paragraphs
paragraphs = [
    "Alice loves hamburgers with extra pickles, and Bob agrees, preferring them with cheese and bacon.",
    "Carol mentions her struggle to find good vegetarian options, while Dave suggests trying a portobello mushroom burger.",
    "Eve shares a challenge of making burgers at home until she found a recipe using breadcrumbs for better texture.",
    "Frank offers a tip about mixing beef and pork for juicier patties, and Grace recommends grilling onions for extra flavor.",
    "Henry concludes by saying that trying different sauces, like aioli or BBQ, can elevate the burger experience."
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


