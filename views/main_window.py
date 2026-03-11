# Fenêtre principale PySide6 avec navigation par menu
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QMenuBar
from PySide6.QtWidgets import QPushButton, QListWidgetItem
from services.auth_service import logout_user
from PySide6.QtGui import QAction
from views.students_view import StudentsViewQt
import sys

class MainWindowQt(QMainWindow):
    def refresh_all(self):
        # Réinitialise l'application et revient à la page de login
        self.clear_layout()
        self.show_login_view()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Application Système de Contrôle (Qt)")
        self.resize(700, 500)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.current_view = None
        self.token = None
        self.username = None
        self.setStyleSheet("""
            QWidget {
                background: #f5f6fa;
                font-family: 'Segoe UI', Arial, sans-serif;
                color: #222;
            }
            QMenuBar, QMenu {
                background: #e0e0e0;
                color: #222;
                font-weight: bold;
            }
            QPushButton {
                background: #e0e0e0;
                color: #222;
                border-radius: 8px;
                padding: 8px 20px;
                font-size: 15px;
                margin: 8px;
            }
            QPushButton:hover {
                background: #cccccc;
            }
            QListWidget, QTableWidget {
                background: #fff;
                border-radius: 8px;
                font-size: 15px;
            }
            QLabel[role='title'] {
                font-size: 22px;
                font-weight: bold;
                color: #888;
                margin: 20px 0 10px 0;
            }
            QLabel[role='subtitle'] {
                font-size: 16px;
                color: #555;
                margin-bottom: 10px;
            }
        """)
        self.create_menu()
        self.show_login_view()

    def create_menu(self):
        menubar = self.menuBar()
        vues_menu = menubar.addMenu("Vues")
        accueil_action = QAction("Accueil", self)
        accueil_action.triggered.connect(self.show_welcome)
        vues_menu.addAction(accueil_action)
        login_action = QAction("Login", self)
        login_action.triggered.connect(self.show_login_view)
        vues_menu.addAction(login_action)
        students_action = QAction("Étudiants", self)
        students_action.triggered.connect(self.show_students_view)
        vues_menu.addAction(students_action)
        # Ajoute ici d'autres interfaces
    def show_login_view(self):
        from views.login_view import LoginViewQt
        self.clear_layout()
        login_view = LoginViewQt(on_success=self.handle_login_success)
        self.layout.addWidget(login_view)
        self.current_view = login_view

    def handle_login_success(self, result):
        # result contient role, token, username, error
        if result.get('error'):
            print("Erreur login:", result['error'])
            return
        self.token = result.get('token')
        self.username = result.get('username')
        print(f"Utilisateur connecté: {self.username}")
        role = result.get('role', '')
        if role == "admin":
            self.show_admin_view()
        else:
            self.show_user_view()

    def show_admin_view(self):
        from PySide6.QtWidgets import QLabel, QListWidget, QListWidgetItem, QPushButton, QHBoxLayout, QVBoxLayout, QFrame
        from PySide6.QtCore import QTimer
        import requests
        self.clear_layout()
        # Layout horizontal pour dashboard
        dashboard_layout = QHBoxLayout()
        # Bloc utilisateurs
        users_frame = QFrame()
        users_frame.setStyleSheet("background: #fff; border-radius: 12px; padding: 16px; margin: 8px;")
        users_layout = QVBoxLayout(users_frame)
        label = QLabel("Utilisateurs connectés")
        label.setProperty('role', 'title')
        users_layout.addWidget(label)
        self.list_widget = QListWidget()
        users_layout.addWidget(self.list_widget)
        dashboard_layout.addWidget(users_frame)
        # Bloc logs récents
        logs_frame = QFrame()
        logs_frame.setStyleSheet("background: #fff; border-radius: 12px; padding: 16px; margin: 8px;")
        logs_layout = QVBoxLayout(logs_frame)
        logs_label = QLabel("Logs d'activité récents")
        logs_label.setProperty('role', 'title')
        logs_layout.addWidget(logs_label)
        self.logs_widget = QListWidget()
        logs_layout.addWidget(self.logs_widget)
        dashboard_layout.addWidget(logs_frame)
        self.layout.addLayout(dashboard_layout)
        # Bouton déconnexion
        logout_btn = QPushButton("Déconnecter")
        logout_btn.setStyleSheet("margin: 10px; font-size: 14px;")
        logout_btn.clicked.connect(self.show_login_view)
        self.layout.addWidget(logout_btn)
        self.current_view = label
        def refresh_dashboard():
            # Rafraîchir utilisateurs
            if hasattr(self, 'list_widget') and self.list_widget is not None:
                self.list_widget.clear()
                users = self.get_users_with_status()
                last_user = None
                for user, is_active in users:
                    if user == last_user:
                        continue
                    item = QListWidgetItem()
                    status = "🟢" if is_active else "⚪"
                    item.setText(f"{status} {user}")
                    self.list_widget.addItem(item)
                    if is_active:
                        btn = QPushButton("Déconnecter")
                        btn.clicked.connect(lambda checked, u=user: self.deconnecter_utilisateur(u))
                        self.layout.addWidget(btn)
                    last_user = user
                    def deconnecter_utilisateur(self, username):
                        # Arrêter le logger d'activité pour cet utilisateur
                        if hasattr(self, 'logger_process') and self.logger_process:
                            self.logger_process.terminate()
                            self.logger_process = None
                        # Appeler l'API pour changer is_active
                        logout_user(username)
                        # Rafraîchir le dashboard
                        self.refresh_all()
            # Rafraîchir logs récents
            if hasattr(self, 'logs_widget') and self.logs_widget is not None:
                self.logs_widget.clear()
                try:
                    resp = requests.get("http://localhost:8000/activity_logs?limit=10")
                    if resp.status_code == 200:
                        logs = resp.json()
                        for log in logs:
                            text = f"{log['start']} | {log['end']} | {log['app']} | {log['username']}"
                            self.logs_widget.addItem(text)
                except Exception:
                    pass
        refresh_dashboard()
        # Rafraîchissement automatique toutes les 5 secondes
        self.admin_timer = QTimer(self)
        self.admin_timer.timeout.connect(refresh_dashboard)
        self.admin_timer.start(5000)

    def get_users_with_status(self):
        import requests
        try:
            response = requests.get("http://localhost:8000/users")
            response.raise_for_status()
            users_data = response.json()
            # On suppose que chaque user a un champ 'username' et 'is_active'
            return [(user['username'], user.get('is_active', False)) for user in users_data]
        except Exception as e:
            print(f"Erreur lors de la récupération des utilisateurs : {e}")
            return []

    def show_user_view(self):
        from PySide6.QtWidgets import QLabel, QPushButton
        import threading, sys, os, subprocess
        self.clear_layout()
        label = QLabel("Bienvenue UTILISATEUR ! Vous êtes connecté à l'interface utilisateur.")
        label.setStyleSheet("font-size: 18px; margin: 20px;")
        self.layout.addWidget(label)
        # Démarrer le logger automatiquement
        import os
        user = self.username or os.environ.get("APP_LOGGED_USER", "user")
        python_path = sys.executable
        script_path = os.path.join('utils', 'activity_logger.py')
        # On passe les arguments sous forme de liste, sans shell=True
        self.logger_process = subprocess.Popen([python_path, script_path])
        # Bouton déconnexion
        logout_btn = QPushButton("Déconnecter")
        logout_btn.setStyleSheet("margin: 10px; font-size: 14px;")
        def logout_and_stop_logger():
            from services.auth_service import logout_user
            import os, platform, subprocess
            # Supprimer la variable d'environnement pour éviter tout envoi résiduel
            if "APP_LOGGED_USER" in os.environ:
                del os.environ["APP_LOGGED_USER"]
            # Arrêter le logger proprement
            if hasattr(self, 'logger_process') and self.logger_process:
                pid = self.logger_process.pid
                try:
                    if platform.system() == 'Windows':
                        subprocess.call(['taskkill', '/F', '/T', '/PID', str(pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    else:
                        self.logger_process.kill()
                    self.logger_process.wait(timeout=5)
                except Exception:
                    pass
                self.logger_process = None
            # Appel à l'endpoint logout avec JWT
            if hasattr(self, 'token') and self.token:
                logout_user(self.token)
            self.username = None
            self.token = None
            print('nom user : non trouvé')
            self.show_login_view()
        logout_btn.clicked.connect(logout_and_stop_logger)
        self.layout.addWidget(logout_btn)
        self.current_view = label

    def show_welcome(self):
        import platform
        from PySide6.QtWidgets import QPushButton
        self.clear_layout()
        system = platform.system()
        label = QLabel(f"Bienvenue dans l'application Système de Contrôle (Qt)\nSystème utilisé : {system}")
        label.setStyleSheet("font-size: 18px; margin: 20px;")
        self.layout.addWidget(label)
        logout_btn = QPushButton("Déconnecter")
        logout_btn.setStyleSheet("margin: 10px; font-size: 14px;")
        logout_btn.clicked.connect(self.show_login_view)
        self.layout.addWidget(logout_btn)
        self.current_view = label

    def show_students_view(self):
        self.clear_layout()
        students_view = StudentsViewQt()
        self.layout.addWidget(students_view)
        self.current_view = students_view

    def clear_layout(self):
        # Arrête le timer admin si actif
        if hasattr(self, 'admin_timer') and self.admin_timer is not None:
            self.admin_timer.stop()
            self.admin_timer = None
        # Supprime le widget de la liste si présent
        if hasattr(self, 'list_widget'):
            self.list_widget = None
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

def run_app_qt():
    app = QApplication(sys.argv)
    window = MainWindowQt()
    window.show()
    sys.exit(app.exec())
