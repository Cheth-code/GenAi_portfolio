# flake8: noqa
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import tool
import requests 
from dotenv import load_dotenv

load_dotenv()
    
@tool()
def get_weather(city: str):
    """ this tool returns the weather of cities of the world"""
    url = f"https://wttr.in/{city}?format=%C+%t"
    response = requests.get(url)

    if response.status_code == 200:
        return f"The weather in {city} is {response.text}."
    
    return "Something went wrong"

tools = [get_weather]


class State(TypedDict):
    messages: Annotated[list, add_messages]
    
    
llm = init_chat_model(model_provider="openai", model="gpt-4.1")    
llm_with_tools = llm.bind_tools(tools)

def chat(state: State):    
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}
    
tool_node = ToolNode(tools=tools)    
graph_builder = StateGraph(State)

graph_builder.add_node("chat", chat)
graph_builder.add_node("tools",tool_node)

graph_builder.add_edge(START, "chat")

graph_builder.add_conditional_edges("chat",tools_condition)

graph_builder.add_edge("tools", "chat")

graph_builder.add_edge("chat",END)

graph = graph_builder.compile()


def main():
    query = input("pls type >: ")
    state = State(
        messages=[{"role": "user", "content": query}]
    )
    for event in graph.stream(state, stream_mode="values"):
        if "messages" in event:
            event["messages"][-1].pretty_print()
            
            
main()    