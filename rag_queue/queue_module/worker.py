# flake8: noqa
from dotenv import load_dotenv
from openai import OpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
load_dotenv()
client = OpenAI()

embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-large",
)

vector_db = QdrantVectorStore.from_existing_collection(
    url="http://vector-db:6333",
    collection_name="my_learing_vector",
    embedding=embedding_model
)
def process_query(query: str):
    print("Seacrhing chunks", query)
    search_res = vector_db.similarity_search(query=query)
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
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYS_PROMPT},
            {"role": "user", "content": query}
        ]
    )    
    print (f" ROBOT 🤖: {query} ", response.choices[0].message.content,"\n\n\n")