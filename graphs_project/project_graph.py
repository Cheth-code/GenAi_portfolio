# flake8: noqa
# from typing_extensions import TypedDict
# from openai import OpenAI
# from typing import Literal
# from dotenv import load_dotenv
# from langgraph.graph import StateGraph, START, END
# from pydantic import BaseModel
import pandas as pd

# load_dotenv()

# client = OpenAI()

# class State(TypedDict):
#     user_input: str
#     llm_result: str | None
    
def read_csv():
    df = pd.read_excel("chethu.xlsx", header=None)  # don't assume header

    # 🔹 Drop completely empty columns and rows
    df = df.dropna(axis=1, how='all')
    df = df.dropna(axis=0, how='all')

    # 🔹 Set the first row as header
    df.columns = df.iloc[0]
    df = df[1:]  # remove that row from data

    print("The Head")
    print(df.head())

    print("The Columns")
    print(df.columns.to_list())

read_csv()
    
        