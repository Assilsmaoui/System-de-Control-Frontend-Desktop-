# Modèle pour un étudiant
from typing import Dict

def parse_student(data: Dict) -> str:
    return f"{data.get('id', '')} - {data.get('name', '')}"
