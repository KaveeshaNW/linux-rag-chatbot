import os
import shutil
import streamlit as st
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

# 1. Page Configuration
st.set_page_config(
    page_title="Linux Assistant Bot",
    page_icon="🐧",
    layout="centered"
)

PERSIST_DIR = "./storage"

# 2. Cached Engine Initialization
@st.cache_resource(show_spinner="Initializing engine & loading Linux index...")
def initialize_engine():
    # Configure Ollama LLM and Embeddings
    Settings.llm = Ollama(model="llama3.2", request_timeout=120.0)
    Settings.embed_model = OllamaEmbedding(model_name="nomic-embed-text")

    # Load existing persistent index or build new one
    if not os.path.exists(PERSIST_DIR):
        documents = SimpleDirectoryReader("./data").load_data()
        index = VectorStoreIndex.from_documents(documents)
        index.storage_context.persist(persist_dir=PERSIST_DIR)
    else:
        storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
        index = load_index_from_storage(storage_context)

    # System Prompt Template
    custom_prompt_tmpl = PromptTemplate(
        "You are a professional Linux Systems Engineer.\n"
        "Use strictly the provided context to answer the user's question.\n"
        "If the answer is not in the context, say 'I don't have information on that in my current Linux documentation.'\n"
        "Always provide exact command syntax, explain the flags, and highlight destructive warnings.\n\n"
        "Context:\n"
        "---------------------\n"
        "{context_str}\n"
        "---------------------\n"
        "User Question: {query_str}\n"
        "Linux Assistant Response: "
    )

    return index.as_query_engine(
        similarity_top_k=2,
        text_qa_template=custom_prompt_tmpl
    )

# Load Query Engine
query_engine = initialize_engine()

# 3. Sidebar Control Panel
with st.sidebar:
    st.header("⚙️ Control Panel")
    
    # Model & Status Info
    st.subheader("System Specs")
    st.markdown("🤖 **LLM:** `llama3.2` (Local)")
    st.markdown("🔍 **Embeddings:** `nomic-embed-text`")
    st.markdown("📁 **Data Source:** `./data/`")
    
    st.divider()

    # Clear Chat History Button
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = [
            {"role": "assistant", "content": "Chat history cleared. How can I help you with Linux?"}
        ]
        st.rerun()

    # Re-index Documents Button
    if st.button("🔄 Re-index Documents", use_container_width=True):
        # 1. Clear Streamlit resource cache
        initialize_engine.clear()
        
        # 2. Delete storage folder to force re-ingestion of ./data/
        if os.path.exists(PERSIST_DIR):
            shutil.rmtree(PERSIST_DIR)
            
        st.toast("Index cleared! Rebuilding from ./data/...", icon="🔄")
        st.rerun()

# 4. Main Chat Header
st.title("🐧 Linux Assistant Bot")
st.caption("A local RAG chatbot powered by Llama 3.2, LlamaIndex, and Ollama.")

# 5. Initialize & Display Chat History
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! Ask me any Linux question (e.g., *'How to check disk usage?'* or *'What is chmod 755?'*)."}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. Handle User Input
if prompt := st.chat_input("Type your Linux question here..."):
    # Append & render user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate & render assistant response
    with st.chat_message("assistant"):
        with st.spinner("Searching docs and generating command..."):
            response = query_engine.query(prompt)
            response_text = str(response)
            st.markdown(response_text)

    # Append response to history
    st.session_state.messages.append({"role": "assistant", "content": response_text})