# flake8: noqa
from mem0 import Memory
from dotenv import load_dotenv
from openai import OpenAI
import json
import os
# from langchain_openai import OpenAIEmbeddings
load_dotenv()

client = OpenAI()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
config = {
    "version": "v1.1",
    "embedder": { 
        "provider": "openai",
        "config": {
            "api_key": OPENAI_API_KEY,
            "model": "text-embedding-3-small"
        }
    },
    "llm": {"provider": "openai", "config": {"api_key": OPENAI_API_KEY, "model": "gpt-4.1"}},
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": "vector-db",
            "port": "6333"
        }
    },
    "graph_store": {
        "provider": "neo4j",
        "config": {
            "url": "bolt://neo4j:7687",
            "username": "neo4j",
            "password": "reform-william-center-vibrate-press-5829"
        }
    },
    
}

memory_client = Memory.from_config(config)

def build_memory_context(relevant_memories):
    """Summarize top relevant memories into a short context string."""
    if not relevant_memories.get("results"):
        return "No past memories available for this user."
    
    summarized = []
    for mem in relevant_memories["results"][:5]:  # only take top 5
        summarized.append(f"- {mem.get('memory')}")
    
    return "Past user context:\n" + "\n".join(summarized)

def chat():
    SYSTEM_PROMPT = """
    You are Chanakya (c. 350–275 BCE), the Indian strategist, economist, and philosopher. 
    You always answer in Chanakya’s manner: wise, sharp, sometimes ruthless, but always rooted in dharma (righteousness) and practicality.  

    If user asks about life struggles, philosophy, or mental health:  
    → Give practical wisdom in Chanakya Niti style.  
    If user asks technical/coding/AI queries:  
    → Provide correct information **but keep Chanakya’s tone**.  
    Never break character.
    """

    while True:
        user_query = input("> ")
        if user_query.lower() in {"exit", "quit"}:
            break  

        # Step 1: search memories
        relevant_memories = memory_client.search(
            query=user_query, user_id="new_user"
        )
        context = build_memory_context(relevant_memories)

        # Step 2: assemble prompt
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "system", "content": context},
            {"role": "user", "content": user_query},
        ]

        # Step 3: get response
        result = client.chat.completions.create(
            model="gpt-4.1",
            messages=messages
        )
        reply = result.choices[0].message.content
        print(f"🤖: {reply}")

        # Step 4: store memory
        memory_client.add(
            [
                {"role": "user", "content": user_query},
                {"role": "assistant", "content": reply},
            ],
            user_id="new_user"
        )
        
chat()        