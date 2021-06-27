import requests

def read_raw_stream(url: str):
    return requests.get(url, stream=True).raw.read()
