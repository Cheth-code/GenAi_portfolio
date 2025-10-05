from pathlib import Path # import pathlib to Path 
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from dotenv import load_dotenv

load_dotenv()
pdf_path = Path(__file__).parent/"node-js.pdf" # file path is provided

loader = PyPDFLoader(file_path=pdf_path) # file path is loaded

docs = loader.load() # .load() loads the pdf and it's metadata

# chunking
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 1000,
    chunk_overlap = 400
)
splitted_docs = text_splitter.split_documents(documents=docs) # splitted documents are loaded

# vector embeddings
embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-large",
)

# now to create a Vector DB to store indexes of [embedding_mode] and [splitted_docs] 

qdrant = QdrantVectorStore.from_documents(
    documents=splitted_docs,
    url="http://vector-db:6333",
    collection_name="my_learing_vector",
    embedding=embedding_model
)

print("Indexing of Documents is Done.....")