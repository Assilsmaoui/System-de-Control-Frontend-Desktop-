def run_app_qt():
    app = QApplication(sys.argv)
    font = QFont("Inter", 10)
    app.setFont(font)
    window = MainWindowQt()
    window.show()
    sys.exit(app.exec())
import sys, os, subprocess
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QLabel, QMenuBar, QPushButton, QGraphicsDropShadowEffect, 
                             QHBoxLayout, QFrame, QMessageBox)
from PySide6.QtGui import QAction, QColor, QFont, QCursor
from PySide6.QtCore import Qt, QSize

class MainWindowQt(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Système de Gestion Professionnel")
        self.resize(1200, 850)
        
        # État de l'utilisateur
        self.username = None
        self.token = None
        self.user_id = None
        self.notif_manager = None
        self._activity_logger_proc = None

        # --- WIDGET CENTRAL ---
        self.central_widget = QWidget()
        self.central_widget.setObjectName("AppBackground")
        self.setCentralWidget(self.central_widget)
        
        # Layout principal sans marges pour le Header collé en haut
        self.main_container = QVBoxLayout(self.central_widget)
        self.main_container.setContentsMargins(0, 0, 0, 0)
        self.main_container.setSpacing(0)

        # 1. Barre de Navigation (Header)
        self.setup_unified_header()

        # 2. Zone de contenu dynamique
        self.content_area = QVBoxLayout()
        self.content_area.setContentsMargins(40, 30, 40, 40)
        self.main_container.addLayout(self.content_area)

        # Appliquer le design global
        self.apply_styles()
        
        # Vue par défaut
        self.show_login_view()

    def setup_unified_header(self):
        """Crée un header blanc moderne avec ombre portée"""
        self.header_frame = QFrame()
        self.header_frame.setObjectName("HeaderFrame")
        self.header_frame.setFixedHeight(80)
        
        # Ombre portée (Drop Shadow) pour l'effet de profondeur
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setYOffset(4)
        self.header_frame.setGraphicsEffect(shadow)

        header_layout = QHBoxLayout(self.header_frame)
        header_layout.setContentsMargins(30, 0, 30, 0)

        # --- GAUCHE : LOGO & NAV ---
        left_layout = QHBoxLayout()
        left_layout.setSpacing(30)

     
        
        self.custom_menu_bar = QMenuBar()
        self.custom_menu_bar.setObjectName("MenuBar")
        
        self.home_action = QAction("Accueil", self)
        self.home_action.triggered.connect(self.show_user_view)
        
        self.tasks_action = QAction("Mes Tâches", self)
        self.tasks_action.triggered.connect(self.show_user_tasks_view)
        
        self.projects_action = QAction("Mes Projets", self)
        self.projects_action.triggered.connect(self.show_user_projects_view)

        self.custom_menu_bar.addAction(self.home_action)
        self.custom_menu_bar.addAction(self.tasks_action)
        self.custom_menu_bar.addAction(self.projects_action)
        
        # left_layout.addWidget(self.logo)  # Suppression du logo (non défini)
        left_layout.addWidget(self.custom_menu_bar)
        header_layout.addLayout(left_layout)

        header_layout.addStretch()

        # --- DROITE : NOTIFICATIONS & PROFIL ---
        right_layout = QHBoxLayout()
        right_layout.setSpacing(15)

        self.notif_btn = QPushButton("🔔")
        self.notif_btn.setObjectName("NotifButton")
        self.notif_btn.setCursor(Qt.PointingHandCursor)
        self.notif_btn.clicked.connect(self.on_notification_clicked)
        
        self.badge_label = QLabel("0")
        self.badge_label.setObjectName("BadgeLabel")
        self.badge_label.setFixedSize(18, 18)
        self.badge_label.setAlignment(Qt.AlignCenter)
        self.badge_label.setVisible(False)

        # Avatar de l'utilisateur
        self.avatar = QPushButton("U")
        self.avatar.setFixedSize(38, 38)
        self.avatar.setStyleSheet("""
            background-color: #4B5563; 
            color: white; 
            border-radius: 19px; 
            font-weight: bold; 
            border: none;
        """)

        right_layout.addWidget(self.notif_btn)
        right_layout.addWidget(self.badge_label)
        right_layout.addSpacing(10)
        right_layout.addWidget(self.avatar)
        
        header_layout.addLayout(right_layout)
        self.main_container.addWidget(self.header_frame)

    def apply_styles(self):
        """Feuille de style globale (QSS) utilisant votre palette"""
        self.setStyleSheet("""
            QWidget#AppBackground { background-color: #F9FAFB; }
            
            QFrame#HeaderFrame { 
                background-color: #FFFFFF; 
                border-bottom: 1px solid #E5E7EB; 
            }
            
            QMenuBar#MenuBar { 
                background: transparent; 
                font-size: 14px; 
                font-weight: 600; 
                color: #6B7280; 
            }
            QMenuBar#MenuBar::item { 
                padding: 10px 20px; 
                background: transparent;
                border-radius: 8px; 
            }
            QMenuBar#MenuBar::item:selected { 
                background-color: #F3F4F6; 
                color: #111827; 
            }

            QPushButton#NotifButton { 
                border: none; 
                background: transparent; 
                font-size: 20px; 
            }
            QPushButton#NotifButton:hover { 
                background-color: #F3F4F6; 
                border-radius: 10px; 
            }

            QLabel#BadgeLabel {
                background-color: #EF4444;
                color: white;
                border-radius: 9px;
                font-size: 9px;
                font-weight: bold;
                margin-left: -22px;
                margin-top: -15px;
            }

            /* Cartes de contenu */
            QFrame#ContentCard {
                background-color: #FFFFFF;
                border-radius: 20px;
                border: 1px solid #E5E7EB;
            }

            /* Bouton Primaire (Design Login) */
            QPushButton#PrimaryAction {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4B5563, stop:1 #1F2937);
                color: white;
                border-radius: 12px;
                padding: 14px 28px;
                font-size: 14px;
                font-weight: bold;
                border: none;
            }
            QPushButton#PrimaryAction:hover { 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #6B7280, stop:1 #374151); 
            }
            QPushButton#PrimaryAction:pressed { background-color: #111827; }
        """)

    def clear_content(self):
        """Nettoie la zone centrale avant d'afficher une nouvelle vue"""
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
        self.avatar.setText(self.username[0].upper() if self.username else "U")
        self.show_user_view()
        if self.user_id:
            self.start_notification_ws(self.user_id)
            self.start_activity_logger()

    def show_user_view(self):
        """Vue Accueil : Bienvenue"""
        self.clear_content()
        card = QFrame()
        card.setObjectName("ContentCard")
        
        # Ombre sur la carte principale
        card_shadow = QGraphicsDropShadowEffect()
        card_shadow.setBlurRadius(30)
        card_shadow.setColor(QColor(0, 0, 0, 15))
        card_shadow.setOffset(0, 8)
        card.setGraphicsEffect(card_shadow)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(60, 60, 60, 60)
        
        name = self.username.capitalize() if self.username else "Utilisateur"
        title = QLabel(f"Bonjour, {name} ")
        title.setStyleSheet("font-size: 32px; font-weight: 800; color: #111827; letter-spacing: -1px;")
        
        subtitle = QLabel("Votre espace de contrôle est prêt. Accédez à vos projets et gérez vos notifications.")
        subtitle.setStyleSheet("font-size: 16px; color: #6B7280; margin-top: 5px; margin-bottom: 30px;")

        logout_btn = QPushButton("Déconnection")
        logout_btn.setObjectName("PrimaryAction")
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.clicked.connect(self.logout_and_stop_logger)
        logout_btn.setFixedWidth(220)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(logout_btn)
        layout.addStretch()

        self.content_area.addWidget(card)

    def show_user_tasks_view(self):
        from views.user_tasks_view import UserTasksViewQt
        self.clear_content()
        tasks_view = UserTasksViewQt(user_id=self.user_id, logout_callback=self.logout_and_stop_logger)
        self.content_area.addWidget(tasks_view)

    def show_user_projects_view(self):
        from views.user_projects_view import UserProjectsViewQt
        self.clear_content()
        projects_view = UserProjectsViewQt(user_id=self.user_id, logout_callback=self.logout_and_stop_logger)
        self.content_area.addWidget(projects_view)

    # --- SERVICES & LOGIQUE ---

    def logout_and_stop_logger(self):
        from services.auth_service import logout_user
        from utils.relaunch import relaunch_app
        if self.token:
            logout_user(self.token)
        self.stop_activity_logger()
        self.close()
        relaunch_app()

    def start_activity_logger(self):
        if not self._activity_logger_proc:
            try:
                path = os.path.join('utils', 'activity_logger.py')
                self._activity_logger_proc = subprocess.Popen([sys.executable, path])
            except Exception as e:
                print(f"Erreur logger: {e}")

    def stop_activity_logger(self):
        if self._activity_logger_proc:
            self._activity_logger_proc.terminate()
            self._activity_logger_proc = None

    def start_notification_ws(self, user_id):
        from views.notification_manager import NotificationManager
        self.notif_manager = NotificationManager(
            self, user_id, self.badge_label, self.notif_btn, self.show_user_tasks_view
        )
        self.notif_manager.start_notification_ws()

    def on_notification_clicked(self):
        if self.notif_manager:
            self.notif_manager.on_notification_clicked()
        else:
            QMessageBox.information(self, "Infos", "Système de notification en cours d'initialisation.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Police système propre
    font = QFont("Inter", 10)
    app.setFont(font)
    
    window = MainWindowQt()
    window.show()
    sys.exit(app.exec())