from flask import Flask, request, Response, stream_with_context
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import marqo
from ai_chat import answer
from typing import List
from knowledge_store import MarqoKnowledgeStore
import document_processors
from document_processors import (
    simple_chunker,
    simple_denewliner,
    sentence_chunker,
    sentence_pair_chunker,
)

app = Flask(__name__)
CORS(app)

INDEX_NAME = "knowledge-management"
CLIENT = marqo.Client("http://localhost:8882")
KNOWLEDGE_ATTR = "knowledge"
CHUNK_SIZE = 512

document_processors.CHUNK_SIZE = CHUNK_SIZE

MKS = MarqoKnowledgeStore(
    CLIENT,
    INDEX_NAME,
    document_chunker=sentence_pair_chunker,
    document_cleaner=simple_denewliner,
)
MKS.reset_index()


def get_document_text(url: str) -> str:
    # Get the HTML content of the webpage
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    # Extract the text from the HTML
    text = soup.get_text()
    return text


@app.route("/getKnowledge", methods=["POST"])
def get_knowledge():
    data = request.get_json()
    q: str = data.get("q")
    limit = data.get("limit")
    return Response(
        stream_with_context(answer(q, MKS, limit)),
        mimetype="text/plain",
    )


@app.route("/addKnowledge", methods=["POST"])
def add_knowledge():
    data = request.get_json()

    # Add the document to the knowledge index
    document = data.get("document")
    MKS.add_document(document)

    return {"message": "Knowledge added successfully"}


@app.route("/addWebpage", methods=["POST"])
def add_webpage():
    data = request.get_json()
    url = data["URL"]

    # Extract the text from the webpage and add it to the knowledge index
    document = get_document_text(url)
    MKS.add_document(document)

    return {"message": "Knowledge added successfully"}
