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

# Nouvelle méthode pour récupérer les tâches d'un utilisateur
def get_user_tasks(user_id):
    try:
        url = f"{BACKEND_URL}/tasks/user/{user_id}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()  # On suppose que la réponse est une liste de tâches
    except requests.RequestException as e:
        return f"Erreur lors de la récupération des tâches: {e}"
