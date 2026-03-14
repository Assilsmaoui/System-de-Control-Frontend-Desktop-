# Fenêtre principale PySide6 avec navigation par menu
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QMenuBar
from PySide6.QtWidgets import QPushButton, QListWidgetItem
from services.auth_service import logout_user
from PySide6.QtGui import QAction
from views.students_view import StudentsViewQt

class MainWindowQt(QMainWindow):
    def show_user_tasks_view(self):
        from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QPushButton, QLabel, QHeaderView
        import requests
        self.clear_layout()
        user_id = getattr(self, 'user_id', None)
        if not user_id or str(user_id) == "None":
            label = QLabel("Aucun utilisateur connecté.")
            self.layout.addWidget(label)
            logout_btn = QPushButton("Déconnecter")
            logout_btn.setStyleSheet("margin: 10px; font-size: 14px;")
            logout_btn.clicked.connect(self.logout_and_stop_logger)
            self.layout.addWidget(logout_btn)
            self.current_view = logout_btn
            return
        label = QLabel("Liste des tâches")
        label.setProperty('role', 'title')
        self.layout.addWidget(label)
        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels(["Titre", "Description", "Priorité", "Début", "Fin", "Statut"])
        table.setStyleSheet("""
            QTableWidget {
                background: #fff;
                border-radius: 12px;
                font-size: 16px;
                margin: 16px 0;
            }
            QHeaderView::section {
                background: #e0e0e0;
                color: #222;
                font-weight: bold;
                font-size: 17px;
                border-radius: 8px;
                padding: 8px;
            }
            QTableWidgetItem {
                padding: 8px;
            }
        """
        )
        table.setMinimumHeight(250)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        from PySide6.QtCore import Qt
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        table.horizontalHeader().setSectionsMovable(True)
        endpoint = f"http://localhost:8000/tasks/user/{user_id}"
        try:
            resp = requests.get(endpoint)
            if resp.status_code == 200:
                tasks = resp.json()
                if isinstance(tasks, list) and tasks:
                    table.setRowCount(len(tasks))
                    for row, task in enumerate(tasks):
                        table.setItem(row, 0, QTableWidgetItem(task.get('title', '')))
                        table.setItem(row, 1, QTableWidgetItem(task.get('description', '')))
                        table.setItem(row, 2, QTableWidgetItem(str(task.get('priority', ''))))
                        table.setItem(row, 3, QTableWidgetItem(task.get('start_date', '')))
                        table.setItem(row, 4, QTableWidgetItem(task.get('end_date', '')))
                        table.setItem(row, 5, QTableWidgetItem(task.get('status', '')))
                else:
                    table.setRowCount(1)
                    table.setItem(0, 0, QTableWidgetItem("Aucune tâche trouvée."))
                    for col in range(1, 6):
                        table.setItem(0, col, QTableWidgetItem(""))
            else:
                table.setRowCount(1)
                table.setItem(0, 0, QTableWidgetItem(f"Erreur lors de la récupération des tâches : {resp.status_code}"))
                for col in range(1, 6):
                    table.setItem(0, col, QTableWidgetItem(""))
        except Exception as e:
            table.setRowCount(1)
            table.setItem(0, 0, QTableWidgetItem(f"Erreur de connexion à l'API : {e}"))
            for col in range(1, 6):
                table.setItem(0, col, QTableWidgetItem(""))
        self.layout.addWidget(table)
        logout_btn = QPushButton("Déconnecter")
        logout_btn.setStyleSheet("margin: 10px; font-size: 14px;")
        logout_btn.clicked.connect(self.logout_and_stop_logger)
        self.layout.addWidget(logout_btn)
        self.current_view = table
    def start_notification_ws(self, user_id):
        import threading
        import websocket
        import json
        def ws_run():
            ws_url = f"ws://localhost:8000/ws/notifications/{user_id}"
            def on_message(ws, message):
                notif = json.loads(message)
                print(f"Notification reçue: {notif}")
                self.notifications.append(notif)
                self.update_notification_badge()
                # Rafraîchir la vue des tâches si elle est affichée
                if hasattr(self, 'current_view') and isinstance(self.current_view, QTableWidget):
                    self.show_user_tasks_view()
                # Affichage popup Qt (notification)
                from PySide6.QtWidgets import QMessageBox
                msg = notif.get('message', str(notif))
                QMessageBox.information(self, "Notification", msg)
            ws = websocket.WebSocketApp(ws_url, on_message=on_message)
            ws.run_forever()
        self.notifications = []
        self.update_notification_badge()
        self.ws_thread = threading.Thread(target=ws_run, daemon=True)
        self.ws_thread.start()

    def update_notification_badge(self):
        count = len(self.notifications)
        if count > 0:
            self.badge_label.setText(str(count))
            self.badge_label.setVisible(True)
        else:
            self.badge_label.setVisible(False)

    def on_notification_clicked(self):
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Notifications", "Aucune notification à afficher.")

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
        # Ajout de l'icône de notification en haut à droite
        from PySide6.QtWidgets import QToolBar, QLabel, QSizePolicy
        from PySide6.QtGui import QIcon, QAction, QPixmap, QPainter, QColor, QFont
        from PySide6.QtCore import Qt
        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.addToolBar(Qt.TopToolBarArea, toolbar)
        # Spacer pour pousser l'icône à droite
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        toolbar.addWidget(spacer)
        # Icône cloche (utilise une icône système ou personnalisée)
        icon = QIcon.fromTheme("bell")
        if icon.isNull():
            pixmap = QPixmap(32, 32)
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            painter.setFont(QFont("Arial", 24))
            painter.setPen(QColor("#222"))
            painter.drawText(pixmap.rect(), Qt.AlignCenter, "🔔")
            painter.end()
            icon = QIcon(pixmap)
        self.notification_action = QAction(icon, "Notifications", self)
        self.notification_action.triggered.connect(self.on_notification_clicked)
        toolbar.addAction(self.notification_action)
        # Badge jaune pour le nombre de notifications non lues (optionnel)
        self.badge_label = QLabel("")
        self.badge_label.setStyleSheet("background: yellow; color: black; border-radius: 10px; font-weight: bold; padding: 2px 6px;")
        self.badge_label.setVisible(False)
        toolbar.addWidget(self.badge_label)
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
        accueil_action.triggered.connect(self.show_user_view)
        vues_menu.addAction(accueil_action)
        # Suppression des actions 'Login' et 'Étudiants' du menu
        # Action pour afficher les tâches utilisateur
        tasks_action = QAction("Tâches utilisateur", self)
        tasks_action.triggered.connect(self.show_user_tasks_view)
        vues_menu.addAction(tasks_action)
        # Ajoute ici d'autres interfaces
        # ...existing code...
    def show_login_view(self):
        from views.login_view import LoginViewQt
        self.clear_layout()
        login_view = LoginViewQt(on_success=self.handle_login_success)
        self.layout.addWidget(login_view)
        self.current_view = login_view

    def handle_login_success(self, result):
        # result contient role, token, username, error, user_id (ObjectId MongoDB)
        print("Résultat login:", result)
        import pprint
        pprint.pprint(result)
        # Affichage du token décodé pour debug
        token = result.get('token')
        if token:
            try:
                import jwt
                decoded = jwt.decode(token, options={"verify_signature": False})
                print("Token décodé:")
                pprint.pprint(decoded)
            except Exception as e:
                print(f"Erreur décodage JWT: {e}")
        if result.get('error'):
            print("Erreur login:", result['error'])
            return
        self.token = result.get('token')
        self.username = result.get('username')
        self.user_id = result.get('user_id')
        print(f"Utilisateur connecté: {self.username} (user_id: {self.user_id})")
        role = result.get('role', '')
        if role == "admin":
            self.show_admin_view()
        else:
            self.show_user_view()
            # Démarrer le WebSocket notifications pour l'utilisateur
            if self.user_id:
                self.start_notification_ws(self.user_id)
            else:
                print("user_id manquant, WebSocket non démarré")

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
        from utils.relaunch import relaunch_app
        logout_btn.clicked.connect(lambda: (self.close(), relaunch_app()))
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
        username = self.username or "Utilisateur"
        label = QLabel(f"Bienvenue {username} ! Vous êtes connecté à l'interface utilisateur.")
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
        logout_btn.clicked.connect(self.logout_and_stop_logger)
        self.layout.addWidget(logout_btn)
        self.current_view = label

    def logout_and_stop_logger(self):
        from utils.relaunch import relaunch_app
        from services.auth_service import logout_user
        import os, platform, subprocess
        # Supprimer la variable d'environnement pour éviter tout envoi résiduel
        if "APP_LOGGED_USER" in os.environ:
            del os.environ["APP_LOGGED_USER"]
        # Tuer tous les activity_logger.py sur le système
        try:
            if platform.system() == 'Windows':
                subprocess.call('taskkill /F /IM python.exe /FI "WINDOWTITLE eq activity_logger.py*"', shell=True)
                # Fallback: kill tous les python qui exécutent activity_logger.py
                subprocess.call('wmic process where "CommandLine like \'%activity_logger.py%\'" call terminate', shell=True)
            else:
                subprocess.call(['pkill', '-f', 'activity_logger.py'])
        except Exception:
            pass
        # Arrêter le logger proprement (processus enfant direct)
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
        self.close()
        relaunch_app()

    def show_welcome(self):
        from PySide6.QtWidgets import QLabel, QPushButton
        self.clear_layout()
        username = self.username or "Utilisateur"
        label = QLabel(f"Bienvenue {username} ! Vous êtes connecté à l'interface utilisateur.")
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
