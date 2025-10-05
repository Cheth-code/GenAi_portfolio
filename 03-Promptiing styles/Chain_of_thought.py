from dotenv import load_dotenv
import json
from openai import OpenAI
load_dotenv()
client = OpenAI()
# CHAIN OF THOUGHT (COT) - The model is encouraged to break down reasoning step by step before arriving at the response
# SYS_PROMPT = """
#     You are an AI very helpful assistant who always reasons before responding to a user query by following these pattern's of thinking in terms of ANALYSE -> THINK -> OUTPUT -> VALIDATE and finally provide the RESULT
#     You must break down the problem in terms of "analyse", "think", "output", "validate" and "result"

#     Example:
#     Input : 3+3 
#     Output: {"step": "analyse", "content": "Alright ! The user is interested in maths query that's an arithmetic operation"}    
#     Output: {"step": "think", "content": "To perform this addition , I must consider two variables and add them"}    
# """
SYS_PROMPT = """
    You are an AI very helpful assistant who always reasons before responding to a user query by following these pattern's of thinking in terms of ANALYSE -> THINK -> OUTPUT -> VALIDATE and finally provide the RESULT
    You must break down the problem in terms of "analyse", "think", "output", "validate" and "result" in JSON format.

    Example:
    Input : 3+3 
    Output: {"step": "analyse", "content": "Alright ! The user is interested in maths query that's an arithmetic operation"}    
    Output: {"step": "think", "content": "To perform this addition , I must consider two variables and add them"}    
    Output: {"step": "output", "content": "3+3 = 6 " }    
    Output: {"step": "validate", "content": "Seems like the answer is 6 , Yeah so the answer is 6 , TO be returned in JSON Format" }    
"""
# response = client.chat.completions.create(
#     model='gpt-4o',
#     response_format={"type":"json_object"},
#     messages=[
#         {"role":'system',"content":SYS_PROMPT},
#         {"role":'user',"content":'Hey, there'},
        
#     ]
# )

messages = [
    {"role": "system", "content":SYS_PROMPT},
]
query = input(">- Pls type your problem: pls add the JSON key word")
messages.append({"role":"user","content":query})
while True:
    response = client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=messages
    )
    messages.append({"role":"assistant","content":response.choices[0].message.content})
    parsed_response = json.loads(response.choices[0].message.content)

    if parsed_response.get("step") != "result":
        print(" thinking",parsed_response.get("content"))
        continue
    print("this is the ans:",parsed_response.get("content"))
    break
