# Service pour interagir avec le backend FastAPI
import requests
from config.settings import BACKEND_URL
from models.backend_response import parse_backend_response

def get_hello_message():
    try:
        response = requests.get(f"{BACKEND_URL}/hello")
        response.raise_for_status()
        return parse_backend_response(response.json())
    except requests.RequestException as e:
        return f"Erreur lors de la connexion au backend: {e}"
