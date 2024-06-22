# ML Pipeline

Speech (audio)
->| Groq -> chopped up text seperated by 25 second segments
->| LLM assisted merge -> sensible long-form block of text
->| Langchain/llama index to genereate Knowledge Graph Triplets -> (SrcEntity, Edge, DstEntity)
->| Yasper/Derek Knowledge Graph Builder -> Full Knowledge Graph & Visualization

Repo - Next JS w/ Uvicorn (FastAPI) and Aceternity UI
