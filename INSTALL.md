# Installation et configuration multi-OS

## Prérequis communs
- Python 3.8+
- pip (installé avec Python)
- Créer un environnement virtuel (recommandé) :
  ```sh
  python -m venv .venv
  # puis activer selon l'OS
  # Windows :
  .venv\Scripts\activate
  # Linux/macOS :
  source .venv/bin/activate
  ```

## Installation des dépendances Python
```sh
pip install -r requirements.txt
```

## Windows
- Dépendances spécifiques :
  - `pywin32` (pour win32gui)
  - `mss` (capture écran)
  - `pyautogui`
- Installer les outils :
  ```sh
  pip install pywin32 mss pyautogui
  ```
- Autoriser l’application dans le pare-feu si besoin (pour accès réseau/API)

## Linux
- Dépendances spécifiques :
  - `xdotool` (détection fenêtre active)
  - `pyscreenshot` (capture écran)
- Installer les paquets système :
  ```sh
  sudo apt-get install xdotool
  # ou équivalent selon la distribution
  ```
- Installer les paquets Python :
  ```sh
  pip install pyscreenshot mss pyautogui
  ```

## macOS
- Dépendances spécifiques :
  - `osascript` (détection fenêtre active, déjà inclus sur macOS)
  - `mss`, `pyautogui`
- Installer les paquets Python :
  ```sh
  pip install mss pyautogui
  ```
- Autoriser l’accès à l’automatisation et à l’enregistrement d’écran dans les Préférences Système > Sécurité et confidentialité

## Backend/API
- S’assurer que le serveur FastAPI/MongoDB est lancé et accessible
- Adapter l’URL de l’API dans le code si besoin

## Lancement de l’application
```sh
python app.py
```

---

**Remarque :**
- Adapter les chemins si besoin selon l’OS
- Tester la capture et la détection de fenêtre sur chaque OS
- Pour toute erreur de dépendance, vérifier les logs et installer le module manquant
