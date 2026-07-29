from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Skutery!"}


# idk should we use uvicorn or somthing like `uv add fastapi[standard] && uv run fastapi dev`. 
# I prefer uvicorn