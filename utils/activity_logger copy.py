import platform
import time
from datetime import datetime
import os
import sys
import requests
import mss
import mss.tools

# ---------------- CONFIG ----------------
log_file = "activityaa_log.txt"
screenshot_dir = "screenshotsaa"
os.makedirs(screenshot_dir, exist_ok=True)

# ---------------- GET USER_ID ----------------
if len(sys.argv) > 1:
    USER_ID = sys.argv[1]
else:
    USER_ID = None

print("OS détecté :", platform.system())
print("USER_ID :", USER_ID)

# ---------------- DETECTION OS ----------------
OS = platform.system()
if OS == "Darwin":
    OS = "macOS"

# ---------------- APP DETECTION ----------------
def get_app_windows():
    try:
        import win32gui
        hwnd = win32gui.GetForegroundWindow()
        if hwnd == 0:
            return ""
        title = win32gui.GetWindowText(hwnd)
        return title.split(" - ")[-1].strip() if " - " in title else title
    except:
        return ""

def get_app_linux():
    try:
        import subprocess
        win_id = subprocess.check_output(["xdotool", "getactivewindow"]).strip()
        pid = subprocess.check_output(["xdotool", "getwindowpid", win_id]).strip()
        return subprocess.check_output(["ps", "-p", pid.decode(), "-o", "comm="]).decode().strip()
    except:
        return ""

def get_app_macos():
    try:
        script = '''
        tell application "System Events"
            get name of first application process whose frontmost is true
        end tell
        '''
        import subprocess
        return subprocess.check_output(["osascript", "-e", script]).decode().strip()
    except:
        return ""

def get_application():
    if OS == "Windows":
        return get_app_windows()
    elif OS == "Linux":
        return get_app_linux()
    elif OS == "macOS":
        return get_app_macos()
    return ""

# ---------------- BROWSER LOG ----------------
def log_browser_window(filename, window_title):
    navigateurs = ["chrome", "firefox", "edge", "opera", "brave"]
    if any(nav in window_title.lower() for nav in navigateurs):
        with open("fenetres_navigateur.txt", "a", encoding="utf-8") as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {window_title} | {filename}\n")

# ---------------- SCREENSHOT ----------------
def take_screenshot(app):
    try:
        filename = ""
        if OS == "Windows":
            import win32gui
            hwnd = win32gui.GetForegroundWindow()
            if hwnd == 0:
                return ""
            title = win32gui.GetWindowText(hwnd)
            safe_name = "".join(c for c in title if c.isalnum() or c in (" ", "_")).rstrip()
            filename = f"{screenshot_dir}/{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            x1, y1, x2, y2 = win32gui.GetWindowRect(hwnd)
            with mss.mss() as sct:
                monitor = {"top": y1, "left": x1, "width": x2 - x1, "height": y2 - y1}
                img = sct.grab(monitor)
                mss.tools.to_png(img.rgb, img.size, output=filename)
            log_screenshot(filename, title)
            log_browser_window(filename, title)
        elif OS == "Linux":
            import pyscreenshot as ImageGrab
            filename = f"{screenshot_dir}/{app}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            ImageGrab.grab().save(filename)
            log_screenshot(filename, app)
            log_browser_window(filename, app)
        elif OS == "macOS":
            filename = f"{screenshot_dir}/{app}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            os.system(f"screencapture -x {filename}")
            log_screenshot(filename, app)
            log_browser_window(filename, app)
        return filename
    except:
        return ""

def log_screenshot(filename, window_title):
    with open("screenshots_log.txt", "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {window_title} | {filename}\n")

# ---------------- LOG ACTIVITY ----------------
def log_short(app, start, end):
    duration = round((end - start).total_seconds(), 2)
    log_data = {
        "start": start.strftime('%Y-%m-%d %H:%M:%S'),
        "end": end.strftime('%Y-%m-%d %H:%M:%S'),
        "app": app,
        "duration": duration,
        "user_id": USER_ID
    }
    already_exists = False
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) >= 5:
                    start_log = parts[0].strip()
                    end_log = parts[1].strip()
                    app_log = parts[2].strip()
                    user_log = parts[-1].replace('user_id:', '').strip()
                    if (start_log == log_data['start'] and end_log == log_data['end'] and app_log == app and user_log == USER_ID):
                        already_exists = True
                        break
    # Envoyer au backend seulement si le user_id existe
    if USER_ID:
        try:
            response = requests.post("http://localhost:8000/activity_logs/", json=log_data)
            response.raise_for_status()
        except Exception:
            pass
    else:
        print("Pas de user_id trouvé, activity_logs non envoyés.")
    if not already_exists:
        # Écriture complète avec la durée
        full_text = f"{log_data['start']}|{log_data['end']}| {app}| {duration} secondes| user_id: {USER_ID}"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(full_text + "\n")

# ---------------- MAIN LOOP ----------------
last_app = ""
last_logged_app = ""
start_time = datetime.now()
captured = False
between_apps = False

while True:
    app = get_application()

    # première détection
    if last_app == "":
        last_app = app
        start_time = datetime.now()
        captured = False
        between_apps = False

    # même application (on attend 5s pour capture éventuelle)
    elif app == last_app:
        duration = (datetime.now() - start_time).total_seconds()
        if duration >= 5 and last_app != last_logged_app:
            take_screenshot(app)
            last_logged_app = last_app

    # changement d’application → enregistrement si durée précédente >= 5s
    else:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        if duration >= 5:
            log_short(last_app, start_time, end_time)
            last_logged_app = last_app
        between_apps = True
        last_app = app
        start_time = datetime.now()
        captured = False

    time.sleep(1)

import platform
import time
from datetime import datetime
import os
import sys
import getpass
import pyautogui
import mss
import mss.tools

# Pour l'envoi HTTP
import requests

# ---------------- CONFIG ----------------
log_file = "activityaa_log.txt"
screenshot_dir = "screenshotsaa"
os.makedirs(screenshot_dir, exist_ok=True)

last_app = ""
last_logged_app = ""
start_time = datetime.now()
captured = False
between_apps = False

# ---------------- DETECTION OS ----------------
OS = platform.system()
if OS == "Darwin":
    OS = "macOS"

# ---------------- GET USER_ID ----------------
if len(sys.argv) > 1:
    USER_ID = sys.argv[1]
else:
    USER_ID = None

print("OS détecté :", OS)
print("USER_ID :", USER_ID)

# ---------------- WINDOWS ----------------
def get_app_windows():
    try:
        import win32gui
        hwnd = win32gui.GetForegroundWindow()
        if hwnd == 0:
            return ""
        title = win32gui.GetWindowText(hwnd)
        return title.split(" - ")[-1].strip() if " - " in title else title
    except:
        return ""

# ---------------- LINUX ----------------
def get_app_linux():
    try:
        import subprocess
        win_id = subprocess.check_output(["xdotool", "getactivewindow"]).strip()
        pid = subprocess.check_output(["xdotool", "getwindowpid", win_id]).strip()
        return subprocess.check_output(["ps", "-p", pid.decode(), "-o", "comm="]).decode().strip()
    except:
        return ""

# ---------------- MACOS ----------------
def get_app_macos():
    try:
        script = '''
        tell application "System Events"
            get name of first application process whose frontmost is true
        end tell
        '''
        import subprocess
        return subprocess.check_output(["osascript", "-e", script]).decode().strip()
    except:
        return ""

# ---------------- DETECTION OS ----------------
OS = platform.system()
if OS == "Darwin":
    OS = "macOS"

# USER_ID is defined below, so we will print it after its definition
print("OS détecté :", OS)

if len(sys.argv) > 1:
    USER_ID = sys.argv[1]
else:
    USER_ID = None

print("USER_ID :", USER_ID)


# ---------------- CAPTURE ÉCRAN ----------------
def take_screenshot(app):
    try:
        filename = ""
        if OS == "Windows":
            import win32gui
            hwnd = win32gui.GetForegroundWindow()
            if hwnd == 0:
                return ""

            title = win32gui.GetWindowText(hwnd)
            safe_name = "".join(c for c in title if c.isalnum() or c in (" ", "_")).rstrip()
            filename = f"{screenshot_dir}/{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

            x1, y1, x2, y2 = win32gui.GetWindowRect(hwnd)
            with mss.mss() as sct:
                monitor = {"top": y1, "left": x1, "width": x2 - x1, "height": y2 - y1}
                img = sct.grab(monitor)
                mss.tools.to_png(img.rgb, img.size, output=filename)
            log_screenshot(filename, title)
            log_browser_window(filename, title)
        elif OS == "Linux":
            import pyscreenshot as ImageGrab
            filename = f"{screenshot_dir}/{app}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            ImageGrab.grab().save(filename)
            log_screenshot(filename, app)
            log_browser_window(filename, app)
        elif OS == "macOS":
            filename = f"{screenshot_dir}/{app}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            os.system(f"screencapture -x {filename}")
            log_screenshot(filename, app)
            log_browser_window(filename, app)
        return filename
    except:
        return ""

def log_screenshot(filename, window_title):
    with open("screenshots_log.txt", "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {window_title} | {filename}\n")

# ---------------- LOG VERSION COURTE ----------------
def log_short(app, start, end):
    duration = round((end - start).total_seconds(), 2)
    log_data = {
        "start": start.strftime('%Y-%m-%d %H:%M:%S'),
        "end": end.strftime('%Y-%m-%d %H:%M:%S'),
        "app": app,
        "duration": duration,
        "user_id": USER_ID
    }
    # Vérifier si une ligne avec exactement le même start, end, app, username existe déjà (ignorer la durée)
    # Vérifier si une ligne avec exactement le même start, end, app, user_id existe déjà (ignorer la durée)
    already_exists = False
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) >= 5:
                    start_log = parts[0].strip()
                    end_log = parts[1].strip()
                    app_log = parts[2].strip()
                    user_log = parts[-1].replace('user_id:', '').strip()
                    if (start_log == log_data['start'] and end_log == log_data['end'] and app_log == app and user_log == USER_ID):
                        already_exists = True
                        break
    # Envoyer au backend seulement si le user_id existe
    if USER_ID:
        try:
            response = requests.post("http://localhost:8000/activity_logs/", json=log_data)
            response.raise_for_status()
        except Exception:
            pass
    else:
        print("Pas de user_id trouvé, activity_logs non envoyés.")
    if not already_exists:
        # Écriture complète avec la durée
        full_text = f"{log_data['start']}|{log_data['end']}| {app}| {duration} secondes| user_id: {USER_ID}"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(full_text + "\n")

# ---------------- BOUCLE PRINCIPALE ----------------
while True:
    app = get_application()

    # première détection
    if last_app == "":
        last_app = app
        start_time = datetime.now()
        captured = False
        between_apps = False

    # même application (on attend 5s pour capture éventuelle)
    elif app == last_app:
        duration = (datetime.now() - start_time).total_seconds()

        if duration >= 5 and last_app != last_logged_app:
            take_screenshot(app)
            last_logged_app = last_app

    # changement d’application → enregistrement si durée précédente >= 5s
    else:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # enregistre seulement si la session précédente a duré au moins 5s
        if duration >= 5:
            log_short(last_app, start_time, end_time)
            last_logged_app = last_app

        between_apps = True
        last_app = app
        start_time = datetime.now()
        captured = False

    time.sleep(1)
