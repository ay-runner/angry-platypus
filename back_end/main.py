# Required Imports
from fastapi import FastAPI
import uvicorn

# Create an instance of the FastAPI class
app = FastAPI()

# Define a route with an endpoint
@app.get("/")
async def root():
    return {
        "message": "Hello World!"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host = "127.0.0.1", 
        port = 8080, 
        reload = True
    )