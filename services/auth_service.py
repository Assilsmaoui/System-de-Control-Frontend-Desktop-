# Service pour l'authentification utilisateur
import requests
from config.settings import BACKEND_URL

import jwt

def logout_user(token):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{BACKEND_URL}/logout", headers=headers)
        response.raise_for_status()
        return True
    except requests.RequestException:
        return False

def login_user(username: str, password: str):
    try:
        response = requests.post(f"{BACKEND_URL}/login", json={"username": username, "password": password})
        response.raise_for_status()
        data = response.json()
        token = data.get("access_token") or data.get("token")
        user_id = data.get("user_id") or data.get("id")
        if token:
            try:
                decoded = jwt.decode(token, options={"verify_signature": False})
                role = decoded.get("role")
                # Extraire user_id du token si absent dans la réponse
                if not user_id:
                    user_id = decoded.get("user_id") or decoded.get("id")
                return {"role": role, "token": token, "username": username, "user_id": user_id, "error": None}
            except Exception as e:
                return {"role": None, "token": token, "username": username, "user_id": user_id, "error": f"Erreur décodage JWT : {e}"}
        return {"role": None, "token": None, "username": username, "user_id": user_id, "error": data.get('message', 'Token manquant')}
    except requests.RequestException as e:
        return {'role': None, 'token': None, 'username': username, 'user_id': None, 'error': f"Erreur de connexion : {e}"}
