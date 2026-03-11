# Exemple de modèle de données pour la réponse du backend
from typing import Dict

def parse_backend_response(data: Dict) -> str:
    return data.get("message", "Aucun message")
