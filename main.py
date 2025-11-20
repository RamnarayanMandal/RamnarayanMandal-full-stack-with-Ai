from typing import Union

from fastapi import FastAPI,Body

from model import Product

from ollama import Client

from promte.chainOfThirthPromoting import SYSTEM_PROMPT


app = FastAPI()

ollama_client = Client(host="http://localhost:11434") 

@app.get("/")
def greet():
    return "Hello, World!"

products = [
    Product(1, "Laptop","this product is a high-end laptop", 999.99, 10),
    Product(2, "Smartphone","this product is a latest model smartphone", 699.99, 25),
    Product(3, "Headphones","this product is noise-cancelling headphones", 199.99, 15),
]

@app.get("/products")
def getall_product():
    return products

@app.post("/chat")
def chat_with_ollama(message: str = Body(..., description="User message")):

    response = ollama_client.chat(
        model="llama3.2",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message},
            
        ]
    )

    return {
        "response": response["message"]["content"]
    }
   
   

