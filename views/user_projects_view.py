from PySide6.QtWidgets import (QFrame, QVBoxLayout, QLabel, QPushButton, 
                             QListWidget, QListWidgetItem, QWidget, 
                             QHBoxLayout, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QColor

class ProjectCard(QFrame):
    """Composant personnalisé pour chaque ligne de projet style SaaS."""
    def __init__(self, projet):
        super().__init__()
        self.setObjectName("ProjectCard")
        
        # Design de la carte projet
        self.setStyleSheet("""
            #ProjectCard {
                background-color: #ffffff;
                border: 1px solid #E5E7EB;
                border-radius: 16px;
                margin: 5px 10px;
            }
            #ProjectCard:hover {
                border: 1px solid #D1D5DB;
                background-color: #F9FAFB;
            }
        """)

        # Effet d'ombre légère pour chaque projet
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 10))
        shadow.setYOffset(2)
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(10)

        # --- Header: Nom + Statut ---
        header_layout = QHBoxLayout()
        
        nom = QLabel(projet.get('nom_projet', 'Projet sans nom'))
        nom.setStyleSheet("font-size: 17px; font-weight: 700; color: #111827;")
        
        # Badge de Statut Dynamique
        statut_text = projet.get('statut', 'En attente').lower()
        statut = QLabel(statut_text.upper())
        statut.setAlignment(Qt.AlignCenter)
        statut.setFixedWidth(110)
        
        # Style des badges identique à la page Tasks
        badge_style = "font-weight: 800; font-size: 10px; border-radius: 10px; padding: 5px;"
        if statut_text == "en cours":
            statut.setStyleSheet(f"{badge_style} background-color: #E0E7FF; color: #3730A3;")
        elif statut_text == "terminé":
            statut.setStyleSheet(f"{badge_style} background-color: #D1FAE5; color: #065F46;")
        else:
            statut.setStyleSheet(f"{badge_style} background-color: #F3F4F6; color: #374151;")
        
        header_layout.addWidget(nom)
        header_layout.addStretch()
        header_layout.addWidget(statut)
        layout.addLayout(header_layout)

        # --- Description ---
        desc = QLabel(projet.get('description', 'Aucune description fournie.'))
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #6B7280; font-size: 14px; line-height: 20px;")
        layout.addWidget(desc)

        # --- Footer: Dates ---
        footer_layout = QHBoxLayout()
        date_info = f"📅 Du {projet.get('date_debut', 'N/A')} au {projet.get('date_fin', 'N/A')}"
        dates = QLabel(date_info)
        dates.setStyleSheet("color: #9CA3AF; font-size: 12px; font-weight: 500;")
        footer_layout.addWidget(dates)
        layout.addLayout(footer_layout)

class UserProjectsViewQt(QFrame):
    def __init__(self, user_id=None, logout_callback=None):
        super().__init__()
        self.user_id = user_id
        self.logout_callback = logout_callback
        self.setup_ui()
        self.fetch_and_display_projects()

    def setup_ui(self):
        self.setObjectName("MainContainer")
        self.setStyleSheet("""
            #MainContainer { background-color: #F9FAFB; }
            
            QListWidget {
                background-color: transparent;
                border: none;
                outline: none;
            }

            /* Style du bouton déconnexion identique au reste de l'app */
            QPushButton#LogoutBtn {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4B5563, stop:1 #1F2937);
                color: #ffffff;
                font-weight: 700;
                font-size: 14px;
                padding: 12px 24px;
                border-radius: 12px;
                border: none;
            }
            QPushButton#LogoutBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #6B7280, stop:1 #374151);
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 20, 40, 40)
        main_layout.setSpacing(0)

        # --- Header de la page ---
        header_section = QVBoxLayout()
        header_section.setContentsMargins(10, 0, 10, 30)
        
        self.title = QLabel("Mes Projets Affectés")
        self.title.setStyleSheet("font-size: 28px; font-weight: 800; color: #111827; letter-spacing: -1px;")
        
        self.subtitle = QLabel("Suivez l'état d'avancement de vos missions et projets en cours.")
        self.subtitle.setStyleSheet("font-size: 16px; color: #6B7280;")
        
        header_section.addWidget(self.title)
        header_section.addWidget(self.subtitle)
        main_layout.addLayout(header_section)

        # --- Liste des Projets ---
        self.projects_list = QListWidget()
        self.projects_list.setSpacing(15) 
        self.projects_list.setVerticalScrollMode(QListWidget.ScrollPerPixel)
        main_layout.addWidget(self.projects_list)

        # --- Footer ---
        if self.logout_callback:
            footer_layout = QHBoxLayout()
            footer_layout.setContentsMargins(0, 30, 0, 0)
            
            self.logout_btn = QPushButton("Déconnection") 
            self.logout_btn.setObjectName("LogoutBtn")
            self.logout_btn.setFixedWidth(220)
            self.logout_btn.setCursor(Qt.PointingHandCursor)
            self.logout_btn.clicked.connect(self.logout_callback)
            
            footer_layout.addStretch()
            footer_layout.addWidget(self.logout_btn)
            main_layout.addLayout(footer_layout)

    def fetch_and_display_projects(self):
        import requests
        self.projects_list.clear()
        
        if not self.user_id:
            self.show_message("Utilisateur non identifié", "#EF4444")
            return

        try:
            # Remplacez par votre constante BACKEND_URL si nécessaire
            url = f"http://localhost:8000/projects/user/{self.user_id}"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            projects = response.json()

            if not projects:
                self.show_message("Aucun projet n'est actuellement assigné à votre compte.")
                return

            for projet in projects:
                item = QListWidgetItem(self.projects_list)
                card = ProjectCard(projet)
                # Ajuste la taille de l'item de la liste à la taille du widget carte
                item.setSizeHint(card.sizeHint())
                self.projects_list.addItem(item)
                self.projects_list.setItemWidget(item, card)

        except Exception as e:
            self.show_message(f"Erreur de synchronisation : {str(e)}", "#EF4444")

    def show_message(self, text, color="#6B7280"):
        label = QLabel(text)
        label.setAlignment(Qt.AlignCenter)
        label.setWordWrap(True)
        label.setStyleSheet(f"color: {color}; font-size: 15px; font-weight: 500; margin-top: 60px;")
        item = QListWidgetItem(self.projects_list)
        item.setSizeHint(QSize(200, 150))
        self.projects_list.addItem(item)
        self.projects_list.setItemWidget(item, label)