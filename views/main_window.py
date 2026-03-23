def run_app_qt():
    app = QApplication(sys.argv)
    window = MainWindowQt()
    window.show()
    sys.exit(app.exec())
import sys, os, subprocess, platform
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QLabel, QMenuBar, QSizePolicy, QPushButton, 
                             QGraphicsDropShadowEffect, QHBoxLayout, QFrame, QMessageBox)
from PySide6.QtGui import QAction, QColor
from PySide6.QtCore import Qt

class MainWindowQt(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Système de Contrôle")
        self.resize(1100, 750)
        
        self.username = None
        self.token = None
        self.user_id = None
        self.notif_manager = None # Initialisation du manager

        # Configuration du widget central
        self.central_widget = QWidget()
        self.central_widget.setObjectName("AppBackground")
        self.setCentralWidget(self.central_widget)
        
        # Layout principal
        self.main_container = QVBoxLayout(self.central_widget)
        self.main_container.setContentsMargins(0, 0, 0, 0)
        self.main_container.setSpacing(0)

        # 1. Header Unifié
        self.setup_unified_header()

        # 2. Zone de contenu
        self.content_area = QVBoxLayout()
        self.content_area.setContentsMargins(40, 30, 40, 40)
        self.main_container.addLayout(self.content_area)

        self.apply_styles()
        self.show_login_view()

    def setup_unified_header(self):
        self.header_frame = QFrame()
        self.header_frame.setObjectName("HeaderFrame")
        self.header_frame.setFixedHeight(75)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 15))
        shadow.setYOffset(3)
        self.header_frame.setGraphicsEffect(shadow)

        header_layout = QHBoxLayout(self.header_frame)
        header_layout.setContentsMargins(30, 0, 30, 0)

        # --- GAUCHE : NAVIGATION ---
        self.custom_menu_bar = QMenuBar()
        self.custom_menu_bar.setObjectName("MenuBar")
        
        self.home_action = QAction("Accueil", self)
        self.home_action.triggered.connect(self.show_user_view)
        
        self.tasks_action = QAction("Mes Tâches", self)
        self.tasks_action.triggered.connect(self.show_user_tasks_view)
        
        self.custom_menu_bar.addAction(self.home_action)
        self.custom_menu_bar.addAction(self.tasks_action)
        
        header_layout.addWidget(self.custom_menu_bar)
        header_layout.addStretch()

        # --- DROITE : NOTIFICATIONS ---
        self.notif_container = QWidget()
        notif_layout = QHBoxLayout(self.notif_container)
        notif_layout.setContentsMargins(0, 0, 0, 0)
        notif_layout.setSpacing(0)

        self.notif_btn = QPushButton("🔔")
        self.notif_btn.setObjectName("NotifButton")
        self.notif_btn.setCursor(Qt.PointingHandCursor)
        self.notif_btn.clicked.connect(self.on_notification_clicked)
        
        self.badge_label = QLabel("0")
        self.badge_label.setObjectName("BadgeLabel")
        self.badge_label.setFixedSize(18, 18)
        self.badge_label.setAlignment(Qt.AlignCenter)
        self.badge_label.setVisible(False)

        notif_layout.addWidget(self.notif_btn)
        notif_layout.addWidget(self.badge_label)
        
        header_layout.addWidget(self.notif_container)
        self.main_container.addWidget(self.header_frame)

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget#AppBackground { background-color: #F3F4F6; }
            QFrame#HeaderFrame { background-color: #FFFFFF; border-bottom: 1px solid #E5E7EB; }
            
            QMenuBar#MenuBar { background: transparent; font-size: 15px; font-weight: 700; color: #4B5563; }
            QMenuBar#MenuBar::item { padding: 10px 20px; border-radius: 8px; margin-right: 10px; color: #4B5563; }
            QMenuBar#MenuBar::item:selected { background-color: #F9FAFB; color: #111827; }

            QPushButton#NotifButton { border: none; background: transparent; font-size: 22px; padding: 8px; }
            QPushButton#NotifButton:hover { background-color: #F3F4F6; border-radius: 20px; }

            QLabel#BadgeLabel {
                background-color: #EF4444; /* Rouge pour les notifications */
                color: white;
                border-radius: 9px;
                font-size: 10px;
                font-weight: bold;
                margin-left: -18px;
                margin-top: -12px;
            }

            QFrame#ContentCard {
                background-color: #FFFFFF;
                border-radius: 20px;
                border: 1px solid #E5E7EB;
            }

            QPushButton#PrimaryAction {
                background-color: #1F2937;
                color: white;
                border-radius: 12px;
                padding: 14px 28px;
                font-weight: bold;
                border: none;
            }
            QPushButton#PrimaryAction:hover { background-color: #374151; }
        """)

    def clear_content(self):
        # Fermer la fenêtre de notifications si elle existe
        if self.notif_manager and hasattr(self.notif_manager, 'list_window'):
            self.notif_manager.list_window.hide()
        while self.content_area.count():
            child = self.content_area.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def show_login_view(self):
        from views.login_view import LoginViewQt
        self.clear_content()
        login_view = LoginViewQt(on_success=self.handle_login_success)
        self.content_area.addWidget(login_view, alignment=Qt.AlignCenter)

    def handle_login_success(self, result):
        self.token = result.get('token')
        self.username = result.get('username')
        self.user_id = result.get('user_id')
        self.show_user_view()
        if self.user_id:
            self.start_notification_ws(self.user_id)
            self.start_activity_logger()

    def show_user_view(self):
        self.clear_content()
        card = QFrame()
        card.setObjectName("ContentCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(50, 50, 50, 50)
        
        name = self.username.capitalize() if self.username else "Utilisateur"
        title = QLabel(f"Bonjour, {name}")
        title.setStyleSheet("font-size: 30px; font-weight: 800; color: #111827; letter-spacing: -1px;")
        
        subtitle = QLabel("Votre espace de contrôle est prêt. Gérez vos tâches et vos notifications.")
        subtitle.setStyleSheet("font-size: 16px; color: #6B7280; margin-top: 5px;")

        logout_btn = QPushButton("Déconnexion")
        logout_btn.setObjectName("PrimaryAction")
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.clicked.connect(self.logout_and_stop_logger)
        logout_btn.setFixedWidth(240)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(30)
        layout.addWidget(logout_btn)
        layout.addStretch()

        self.content_area.addWidget(card)

    def show_user_tasks_view(self):
        from views.user_tasks_view import UserTasksViewQt
        self.clear_content()
        # On passe l'ID utilisateur et le callback de déconnexion
        tasks_view = UserTasksViewQt(user_id=self.user_id, logout_callback=self.logout_and_stop_logger)
        self.content_area.addWidget(tasks_view)

    def logout_and_stop_logger(self):
        from services.auth_service import logout_user
        from utils.relaunch import relaunch_app
        if self.token:
            logout_user(self.token)
        self.stop_activity_logger()
        self.close()
        relaunch_app()

    def start_activity_logger(self):
        import subprocess
        import sys
        # Démarre le logger d'activité dans un sous-processus
        if not hasattr(self, '_activity_logger_proc') or self._activity_logger_proc is None:
            self._activity_logger_proc = subprocess.Popen([sys.executable, os.path.join('utils', 'activity_logger.py')])

    def stop_activity_logger(self):
        # Arrête le logger d'activité si lancé
        if hasattr(self, '_activity_logger_proc') and self._activity_logger_proc:
            try:
                self._activity_logger_proc.terminate()
            except Exception:
                pass
            self._activity_logger_proc = None

    def start_notification_ws(self, user_id):
        from views.notification_manager import NotificationManager
        # Mise à jour de l'appel avec le bouton notif pour le positionnement
        self.notif_manager = NotificationManager(
            self, 
            user_id, 
            self.badge_label, 
            self.notif_btn, 
            self.show_user_tasks_view
        )
        self.notif_manager.start_notification_ws()

    def on_notification_clicked(self):
        if self.notif_manager:
            self.notif_manager.on_notification_clicked()
        else:
            QMessageBox.information(self, "Infos", "Système de notification non initialisé.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindowQt()
    window.show()
    sys.exit(app.exec())