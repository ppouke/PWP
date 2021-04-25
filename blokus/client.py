import pygame
import requests

API_URL = "http://127.0.0.1:5000/"

def getBlocks(s, blocks_href):
    resp = s.get(API_URL + blocks_href)
    body = resp.json()
    blocks = []
    for i in body['items']:
        r = s.get(API_URL + i['@controls']['self']['href'])
        b=r.json()
        blocks.append(b['shape'])
    return blocks



if __name__ == "__main__":
    with requests.Session() as s:
        s.headers.update({"Accept": "application/vnd.mason+json"})
        resp = s.get(API_URL + "/api/")
        if resp.status_code != 200:
            print("Unable to access API")
        else:
            body = resp.json()
            blocks = getBlocks(s, body['@controls']['blokus:blocks-all']['href'])
            