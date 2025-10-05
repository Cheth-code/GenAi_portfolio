import os
import asyncio
from typing import List
import bs4
from dotenv import load_dotenv
from langchain_community.document_loaders import WebBaseLoader
from langchain_unstructured import UnstructuredLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
import qdrant_client

load_dotenv()
URLS = [
    # use any pages you like; this one is from the docs’ example
    "https://python.langchain.com/docs/how_to/chatbots_memory/",
    # add more pages if desired
]
os.environ.setdefault(
    "USER_AGENT",
    "ChethanWebLoader/1.0 (+https://github.com/your-handle; contact: you@example.com)",
)
async def load_simple(urls: List[str]):
    loader = WebBaseLoader(
        web_paths=urls,
        # Optional: precisely target the article body using SoupStrainer
        bs_kwargs={
            "parse_only": bs4.SoupStrainer(class_="theme-doc-markdown markdown"),
        },
        # Optional: control whitespace / separators
        bs_get_text_kwargs={"separator": " | ", "strip": True},
    )

    docs = []
    async for doc in loader.alazy_load():
        docs.append(doc)
    return docs

async def load_advanced(url: str):
    loader = UnstructuredLoader(web_url=url)
    docs = []
    async for doc in loader.alazy_load():
        docs.append(doc)
    return docs

def build_retriever(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200, chunk_overlap=150, separators=["\n\n", "\n", " ", ""]
    )
    chunks = splitter.split_documents(docs)

    embeddings = OpenAIEmbeddings()
    client = qdrant_client.QdrantClient(
        url = "http://localhost:6333",
    )  
    vs = QdrantVectorStore.from_documents(
        documents=chunks,
        embedding=embeddings,
        client=client,
        collection_name="web_rag_collection",
    )
    return vs.as_retriever(search_k=5)

async def main():
    print("\n=== SIMPLE & FAST (WebBaseLoader) ===")
    simple_docs = await load_simple(URLS)
    print(f"Loaded {len(simple_docs)} document(s).")
    if simple_docs:
        d = simple_docs[0]
        print("Meta:", {k: d.metadata.get(k) for k in ["source", "title", "language"]})
        print("Preview:", d.page_content[:300], "...\n")

    print("\n=== ADVANCED (UnstructuredLoader) ===")
    adv_docs_all = []
    for u in URLS[:1]:  # show on the first URL for brevity
        adv_docs = await load_advanced(u)
        adv_docs_all.extend(adv_docs)
    print(f"Advanced loader produced {len(adv_docs_all)} structured elements.")
    if adv_docs_all:
        # Print first few categories to show structure
        for i, d in enumerate(adv_docs_all[:5]):
            print(f"[{i}] category={d.metadata.get('category')} :: {d.page_content[:120]}...")

    # ---- Optional: build a retriever and ask something ----
    try:
        print("\n=== OPTIONAL: Build retriever & ask a question ===")
        combined = simple_docs + adv_docs_all
        retriever = build_retriever(combined)
        query = "What are common ways to add memory to chatbots?"
        print("Query:", query)
        results = retriever.invoke(query)
        for i, r in enumerate(results):
            print(f"\nTop {i+1} chunk from:", r.metadata.get("source"))
            print(r.page_content[:300], "...")
    except Exception as e:
        print("(Skipping retrieval demo) Reason:", e)


if __name__ == "__main__":
    asyncio.run(main())
