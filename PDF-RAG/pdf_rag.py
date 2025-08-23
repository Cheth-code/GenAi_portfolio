
from openai import OpenAI
import streamlit as st
from pathlib import Path
import tempfile
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore



# Load environment variables
load_dotenv()

st.set_page_config(page_title="📚 PDF AI RAG with Qdrant", page_icon="🤖", layout="wide")
st.title("📚 PDF AI RAG with Qdrant")
st.write("Upload a PDF, index it into Qdrant, and chat with your document using AI.")

# Initialize OpenAI client
client = OpenAI()

# Embedding model
embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-large",
)

# -----------------------------
# Chat History Initialization
# -----------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # stores tuples: (role, message)

# -----------------------------
# PDF Upload & Indexing
# -----------------------------
st.sidebar.header("📄 Upload & Index PDF")
uploaded_file = st.sidebar.file_uploader("Upload your PDF", type="pdf")

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = Path(tmp_file.name)

    if st.sidebar.button("Index to Qdrant"):
        with st.spinner("Indexing your PDF into Qdrant..."):
            loader = PyPDFLoader(file_path=tmp_path)
            docs = loader.load()

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=400
            )
            splitted_docs = text_splitter.split_documents(documents=docs)

            qdrant = QdrantVectorStore.from_documents(
                documents=splitted_docs,
                url="http://localhost:6333",
                collection_name="my_learning_vector",
                embedding=embedding_model
            )

        st.sidebar.success("✅ Indexing of Documents is Done!")
        st.sidebar.write(f"Total Chunks Indexed: {len(splitted_docs)}")
        st.sidebar.subheader("Metadata Preview")
        st.sidebar.json(splitted_docs[0].metadata if splitted_docs else {})

# -----------------------------
# Chat Interface
# -----------------------------
st.header("💬 Chat with your Document")

# Display previous chat history
for role, message in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(message)

# Chat input
if prompt := st.chat_input("Ask a question about the uploaded PDF:"):
    # Add user message to chat history
    st.session_state.chat_history.append(("user", prompt))
    with st.chat_message("user"):
        st.markdown(prompt)

    # Connect to existing Qdrant collection
    vector_db = QdrantVectorStore.from_existing_collection(
        url="http://localhost:6333",
        collection_name="my_learning_vector",
        embedding=embedding_model
    )

    # Search in Qdrant
    search_res = vector_db.similarity_search(query=prompt)

    # Build context from search results
    content_context = "\n\n".join([
        f"Page content: {result.page_content}\n"
        f"Page Number: {result.metadata.get('page_label', 'N/A')}\n"
        f"Source: {result.metadata.get('source', 'N/A')}"
        for result in search_res
    ])

    # System prompt
    SYS_PROMPT = f"""
        You are a helpful AI Assistant who answers user queries based on the provided context 
        retrieved from a PDF file along with page_contents and page number.

        You must only answer the user based on the following context and guide them 
        to the right page to know more.

        Context:
        {content_context}
    """

    # Call GPT model
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYS_PROMPT},
            *[{"role": role, "content": msg} for role, msg in st.session_state.chat_history],
            {"role": "user", "content": prompt}
        ]
    )

    answer = response.choices[0].message.content

    # Add AI message to chat history
    st.session_state.chat_history.append(("assistant", answer))
    with st.chat_message("assistant"):
        st.markdown(answer)
