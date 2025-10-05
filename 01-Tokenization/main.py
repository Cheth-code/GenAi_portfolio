import tiktoken
enc = tiktoken.encoding_for_model('gpt-4o')
text = input("Enter your text to be coonverted into Tokens\n")
tokens = enc.encode(text)
print("Tokens: ",tokens ) 
decode_tokens = enc.decode(tokens)
print("Decode tokens: ", decode_tokens)