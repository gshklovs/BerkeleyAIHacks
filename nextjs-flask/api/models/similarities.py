from transformers import BertModel, BertTokenizer
import torch.nn.functional as F
import torch

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

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