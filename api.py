import json

from fastapi import FastAPI, HTTPException
import os

from starlette.responses import RedirectResponse

app = FastAPI()

@app.get("/", include_in_schema=False)
def redirect_to_docs():
    return RedirectResponse(url="/docs")

@app.get("/v2/", include_in_schema=False)
def redirect_to_docs():
    return RedirectResponse(url="/docs")

@app.get("/v2/{id_}")
def read_data(id_: str):
    data_file = os.path.join("data", "v2", f"{id_}.json")
    if os.path.exists(data_file):
        with open(data_file, 'r') as f:
            data = json.load(f)
        return data
    else:
        raise HTTPException(status_code=200, detail="Data not found")
