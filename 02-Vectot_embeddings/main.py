from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()

client = OpenAI()
response = client.responses.create(
    model="gpt-4",
    input = "Write a great anictode on luck within limited sentences"
)
print(response.output_text)

