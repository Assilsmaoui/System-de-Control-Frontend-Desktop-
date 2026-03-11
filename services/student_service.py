# Service pour récupérer la liste des étudiants
import requests
from config.settings import BACKEND_URL
from models.student import parse_student

def get_students():
    try:
        response = requests.get(f"{BACKEND_URL}/students")
        response.raise_for_status()
        students = response.json()
        return [parse_student(s) for s in students]
    except requests.RequestException as e:
        return [f"Erreur lors de la connexion au backend: {e}"]
