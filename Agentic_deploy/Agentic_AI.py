from dotenv import load_dotenv
from openai import OpenAI
import requests
import json
import os

load_dotenv()

client = OpenAI()

def run_command(cmd: str):
    result = os.system(cmd)
    return result

def get_weather(city: str):
    url = f"https://wttr.in/{city}?format=%C+%t"
    response = requests.get(url)

    if response.status_code == 200:
        return f"The weather in {city} is {response.text}."
    
    return "Something went wrong"

available_tools = {
    "get_weather": get_weather,
    "run_command": run_command,
}

SYSTEM_PROMPT = """
    You are an helpful AI Assistant who is specialized in resolving user query.
    You work on start, plan, action, observe mode.

    For the given user query and available tools, plan the step by step execution, based on the planning,
    select the relevant tool from the available tool. and based on the tool selection you perform an action to call the tool.

    Wait for the observation and based on the observation from the tool call resolve the user query.
    Always create new folder in a new terminal for app suggestions or recommendations and check for whether the required libraries are present, if not install them by asking the user permissions
    
    Also run the file is possible  

    Rules:
    - Follow the Output JSON Format.
    - Always perform one step at a time and wait for next input
    - Carefully analyse the user query

    Output JSON Format:
    {{
        "step": "string",
        "content": "string",
        "function": "The name of function if the step is action",
        "input": "The input parameter for the function",
    }}

    Available Tools:
    - "run_command": Takes Windows CMD/PowerShell command as a string and executes the command and returns the output after executing it.

    Example 1:
    User Query: What is the weather of new york?
    Output: {{ "step": "plan", "content": "The user is interested in weather data of new york" }}
    Output: {{ "step": "plan", "content": "From the available tools I should call get_weather" }}
    Output: {{ "step": "action", "function": "get_weather", "input": "new york" }}
    Output: {{ "step": "observe", "output": "12 Degree Cel" }}
    Output: {{ "step": "output", "content": "The weather for new york seems to be 12 degrees." }}

    Example 2:
    { "step": "plan", "content": "The user is interested in creating a TODO app" }
    { "step": "plan", "content": "From the available tools I should call run_command to create a project folder for the app" }
    { "step": "action", "function": "run_command", "input": "mkdir TODO-APP" }
    { "step": "observe", "output": "Created folder TODO-APP" }
    { "step": "plan", "content": "Now I should create a Python file for the Streamlit TODO app" }
    { "step": "action", "function": "run_command", "input": "echo \"import streamlit as st\n\nst.title('TO-DO-LIST')\n\ntask = st.text_input('Enter your task', ' ')\n\nif 'task_list' not in st.session_state:\n    st.session_state['task_list'] = []\n\nif st.button('Add your task\\'s'):\n    if task:\n        st.session_state['task_list'].append(task)\n\nfor i, t in enumerate(st.session_state['task_list']):\n    st.write(f'{i+1}. {t}')\n\nfor i, t in enumerate(st.session_state['task_list']):\n    if st.checkbox(f'{i+1}. {t}'):\n        st.session_state['task_list'].remove(t)\" > TODO-APP/todo_app.py" }
    { "step": "observe", "output": "todo_app.py file created successfully" }
    { "step": "plan", "content": "Now I should run the Streamlit app to launch the TODO application" }
    { "step": "action", "function": "run_command", "input": "streamlit run TODO-APP/todo_app.py" }
    { "step": "output", "content": "Your TODO-APP is built and running at the provided local URL." }

   
"""

messages = [
  { "role": "system", "content": SYSTEM_PROMPT }
]

while True:
    query = input("> Hey I'm a TODO AI builder: ")
    messages.append({ "role": "user", "content": query })

    while True:
        response = client.chat.completions.create(
            model="gpt-4.1",
            response_format={"type": "json_object"},
            messages=messages
        )

        messages.append({ "role": "assistant", "content": response.choices[0].message.content })
        parsed_response = json.loads(response.choices[0].message.content)

        if parsed_response.get("step") == "plan":
            print(f"🧠: {parsed_response.get("content")}")
            continue

        if parsed_response.get("step") == "action":
            tool_name = parsed_response.get("function")
            tool_input = parsed_response.get("input")

            print(f"🛠️: Calling Tool:{tool_name} with input {tool_input}")

            if available_tools.get(tool_name) != False:
                output = available_tools[tool_name](tool_input)
                messages.append({ "role": "user", "content": json.dumps({ "step": "observe", "output": output }) })
                continue
        
        if parsed_response.get("step") == "output":
            print(f"🤖: {parsed_response.get("content")}")
            break