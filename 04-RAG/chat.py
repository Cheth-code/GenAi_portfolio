from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

# Embedding model
embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-large",
)

# Connect to existing Qdrant collection
vector_db = QdrantVectorStore.from_existing_collection(
    url="http://localhost:6333",
    collection_name="my_learing_vector",
    embedding=embedding_model
)

print("💬 Chat interface ready! Type 'exit' to quit.\n")

while True:
    query = input("> ").strip()
    if query.lower() in ["exit", "quit"]:
        print("👋 Goodbye!")
        break

    # Search Qdrant for relevant chunks
    search_res = vector_db.similarity_search(query=query)

    # Prepare context from retrieved chunks
    content_context = "\n\n".join([
        f"Page content: {result.page_content}\n"
        f"Page Number: {result.metadata.get('page_label', 'N/A')}\n"
        f"Source: {result.metadata.get('source', 'N/A')}"
        for result in search_res
    ])

    # System prompt for GPT
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
            {"role": "user", "content": query}
        ]
    )

    # Print only the text content of GPT's answer
    print(f"🤖: {response.choices[0].message.content}\n")
