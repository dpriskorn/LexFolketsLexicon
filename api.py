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


@app.get("/v2/word/{id_}")
def read_word_data(id_: str):  # dead: disable
    """It returns 200 and empty dictionary if the record is not found"""
    data_file = os.path.join("data", "v2", "word", f"{id_}.json")
    if os.path.exists(data_file):
        with open(data_file, "r") as f:
            data = json.load(f)
        return data
    else:
        return {}


@app.get("/v2/idiom/{id_}")
def read_idiom_data(id_: str):  # dead: disable
    """It returns 200 and empty dictionary if the record is not found"""
    data_file = os.path.join("data", "v2", "idiom", f"{id_}.json")
    if os.path.exists(data_file):
        with open(data_file, "r") as f:
            data = json.load(f)
        return data
    else:
        return {}


@app.get("/v2/example/{id_}")
def read_example_data(id_: str):  # dead: disable
    """It returns 200 and empty dictionary if the record is not found"""
    data_file = os.path.join("data", "v2", "example", f"{id_}.json")
    if os.path.exists(data_file):
        with open(data_file, "r") as f:
            data = json.load(f)
        return data
    else:
        return {}
