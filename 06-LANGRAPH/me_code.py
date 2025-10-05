# flake8: noqa

from typing_extensions import TypedDict
from openai import OpenAI
from typing import Literal
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel

load_dotenv()
client = OpenAI()

class classifymessageofuser(BaseModel):
    is_it_a_code_qury: bool
    
class codeaccuracy(BaseModel):
    accuracy: float 

class State(TypedDict):
    users_query: str
    gpt_res: str | None
    is_it_a_code_qury: bool | None
    accuracy: float | None
    retries: int
    
def classify_user_query(state: State):
    print("⚠️ classify_message")
    query = state['users_query']
    SYSTEM_PROMPT = """
    You are an classifying AI agent. Your main task is to classify the user's input query into categories,
    you can find your're own categories but you have rectify it was a coding_query or any other one.
    Return the respone in specified JSON boolean form only. 
    """
    response = client.beta.chat.completions.parse(
        model="gpt-4.1-nano",
        response_format=classifymessageofuser,
        messages=[
            {"role":"system","content": SYSTEM_PROMPT},
            {"role":"user","content": query},
        ]
    )
    is_it_a_code_qury = response.choices[0].message.parsed.is_it_a_code_qury
    state["is_it_a_code_qury"] = is_it_a_code_qury
    return state

def route_query(state:State) -> Literal ["general_query","code_query"]:
    print("⚠️ route_query")
    is_code = state["is_it_a_code_qury"]
    
    if is_code:
        return "code_query"
    
    return "general_query"
    
def general_query(state: State):
    print("⚠️ general_query")
    query = state["users_query"]
    SYSTEM_PROMPT = """
        You are an Generalist AI Agent. Your task is to deal with the user questions, by providing them a generalist approach
        You posses immense amount of generalist behaviour and answer the user queries
    """
    response = client.chat.completions.create(
        model="gpt-4.1-mini-2025-04-14",
        messages=[
            {"role":"system","content": SYSTEM_PROMPT},
            {"role":"user","content": query},
        ]
    )    
    state["gpt_res"] = response.choices[0].message.content
    return state

def code_query(state: State):
    print("⚠️ code_query")
    query = state["users_query"]
    SYSTEM_PROMPT = """
        You are an Expert Coding AI Agent. Your task is to deal with the user questions that's realted to code questions, by providing them an parsimounious code with an simple explanation at last. 
        You posses immense knowledge of Coding, Debuggin skills that would help the user in resolving his code queries
    """
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role":"system","content": SYSTEM_PROMPT},
            {"role":"user","content": query},
        ]
        
    )
    state["gpt_res"] = response.choices[0].message.content
    
    return state

def code_validator(state: State):
    print("⚠️ code_validator")
    query = state["users_query"]
    llm_code = state["gpt_res"]
    
    SYSTEM_PROMPT = f"""
        You are expert in calculating accuracy of the code according to the question.
        Return the percentage of accuracy
        
        User Query: {query}
        Code: {llm_code}
    """
    response = client.beta.chat.completions.parse(
        model="gpt-4.1-nano-2025-04-14",
        response_format=codeaccuracy,
        messages=[
            {"role":"system","content": SYSTEM_PROMPT},
            {"role":"user","content": query},
        ]
    )
    state["accuracy"] = response.choices[0].message.parsed.accuracy
    return state

def accuracy_compare(state: State):
    print("⚠️ accuracy_comparing")
    accuracy_percentage = state.get("accuracy", 0)
    retries = state.get("retries", 0)

    if accuracy_percentage < 90 and retries < 3:
        retries += 1
        state["retries"] = retries
        print(f"🔁 Retry {retries}, accuracy={accuracy_percentage}")
        if retries == 3:
            print(f"❌ Retries {retries} reached a limit")
            return state
    else:
        print(f"✅ Accuracy acceptable . accuracy={accuracy_percentage}")
    
    return state   # 👈 always return the dict

def accuracy_router(state: State) -> str:
    if state["accuracy"] < 90 and state["retries"] < 3:
        state["retries"] += 1
        print(f"🔁 Retry {state['retries']}, accuracy={state['accuracy']}")
        return "code_query"
    return END  # END is fine here, type hint is just str


graph_builder = StateGraph(State)
# TO DEFINE NODES
graph_builder.add_node("classify_user_query",classify_user_query)
graph_builder.add_node("route_query",route_query)
graph_builder.add_node("general_query",general_query)
graph_builder.add_node("code_query",code_query)
graph_builder.add_node("code_validator",code_validator)
graph_builder.add_node("accuracy_compare",accuracy_compare)
graph_builder.add_node("accuracy_router",accuracy_router)

# Flow: START → classify → route → (general_query or code_query)
graph_builder.add_edge(START, "classify_user_query")
graph_builder.add_conditional_edges("classify_user_query", route_query)

# General query → END
graph_builder.add_edge("general_query", END)

# Code query → validator
graph_builder.add_edge("code_query", "code_validator")

# Validator → accuracy compare
graph_builder.add_edge("code_validator", "accuracy_compare")

# Accuracy compare → conditional routing (retry or end)
graph_builder.add_conditional_edges("accuracy_compare", accuracy_router)

graph = graph_builder.compile()

def main():
    user = input("> I'm ready : ")
    _state = State = {
        "users_query": user,
        "gpt_res": None,
        "is_it_a_code_qury": False,
        "accuracy": None,
        "retries": 0,
    } 
    for event in graph.stream(_state):
        print("Event", event)
    

main()        