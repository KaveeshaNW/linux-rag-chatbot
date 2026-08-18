import os
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
    Settings,
    PromptTemplate,
)
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding

# 1. Configure local Ollama LLM and Embeddings
Settings.llm = Ollama(model="llama3.2", request_timeout=120.0)
Settings.embed_model = OllamaEmbedding(model_name="nomic-embed-text")

PERSIST_DIR = "./storage"

# 2. Build or Load the Persistent Index
if not os.path.exists(PERSIST_DIR):
    print("🔄 Indexing documents for the first time...")
    documents = SimpleDirectoryReader("./data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    index.storage_context.persist(persist_dir=PERSIST_DIR)
    print("✅ Index created and saved to disk.")
else:
    print("⚡ Loading existing index from storage...")
    storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
    index = load_index_from_storage(storage_context)
    print("✅ Index loaded.")

# 3. Create System Prompt Template for Accuracy
custom_prompt_tmpl = PromptTemplate(
    "You are a professional Linux Systems Engineer.\n"
    "Use strictly the provided context to answer the user's question.\n"
    "If the answer is not in the context, say 'I don't have information on that in my current Linux docs.'\n"
    "Always provide exact command syntax, flag explanations, and highlight destructive warnings.\n\n"
    "Context:\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "User Question: {query_str}\n"
    "Linux Assistant Response: "
)

# 4. Initialize Query Engine
query_engine = index.as_query_engine(
    similarity_top_k=2,
    text_qa_template=custom_prompt_tmpl,
)

# 5. CLI Chat Loop
print("\n==============================================")
print("🐧 Local Linux Assistant Ready! (Type 'exit' to quit)")
print("==============================================\n")

while True:
    try:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ["exit", "quit", "q"]:
            print("Exiting...")
            break

        print("\nThinking...")
        response = query_engine.query(user_input)
        print(f"\nAssistant:\n{response}\n")
        print("-" * 45)

    except KeyboardInterrupt:
        print("\nExiting...")
        break