import json
import os

from fastapi import FastAPI
from starlette.responses import RedirectResponse

app = FastAPI()


@app.get("/", include_in_schema=False)
def redirect_to_docs():  # dead: disable
    return RedirectResponse(url="/docs")


@app.get("/v2/", include_in_schema=False)
def redirect_to_docs2():  # dead: disable
    return RedirectResponse(url="/docs")


@app.get("/v2/{id_}")
def read_data(id_: str):  # dead: disable
    """It returns 200 and empty dictionary if the record is not found"""
    data_file = os.path.join("data", "v2", f"{id_}.json")
    if os.path.exists(data_file):
        with open(data_file, "r") as f:
            data = json.load(f)
        return data
    else:
        return {}
