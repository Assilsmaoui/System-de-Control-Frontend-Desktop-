# Modèle pour une tâche utilisateur
from typing import Dict

class Task:
    def __init__(self, data: Dict):
        self.id = data.get('id')
        self.title = data.get('title', '')
        self.description = data.get('description', '')
        self.priority = data.get('priority', '')
        self.start_date = data.get('start_date', '')
        self.end_date = data.get('end_date', '')
        self.status = data.get('status', '')

    def __str__(self):
        return f"Titre : {self.title}\nDescription : {self.description}\nPriorité : {self.priority}\nDébut : {self.start_date}\nFin : {self.end_date}\nStatut : {self.status}"