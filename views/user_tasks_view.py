import requests
from config.settings import BACKEND_URL
from datetime import datetime
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, 
                             QTableWidgetItem, QPushButton, QHeaderView, QFrame, 
                             QMessageBox, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor

class UserTasksViewQt(QWidget):
    def __init__(self, user_id, logout_callback=None, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.logout_callback = logout_callback
        self._is_syncing_overdue = False
        
        # Layout principal de la vue
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.apply_styles()
        self.init_ui()

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget { background-color: transparent; font-family: 'Inter', 'Segoe UI', sans-serif; }
            
            /* Carte principale style SaaS */
            QFrame#MainCard {
                background-color: #FFFFFF;
                border-radius: 20px;
                border: 1px solid #E5E7EB;
            }

            QLabel#TitleLabel {
                font-size: 24px; 
                font-weight: 800; 
                color: #1F2937; 
                letter-spacing: -1px;
            }

            /* Style de la Table */
            QTableWidget {
                background-color: transparent;
                border: none;
                gridline-color: #F3F4F6;
                font-size: 13px;
                color: #4B5563;
                selection-background-color: #F9FAFB;
                selection-color: #1F2937;
            }

            QHeaderView::section {
                background-color: #F9FAFB;
                padding: 15px;
                border: none;
                border-bottom: 2px solid #F3F4F6;
                font-weight: 700;
                color: #9CA3AF;
                text-transform: uppercase;
                font-size: 11px;
            }

            /* Boutons d'Action dans la table */
            QPushButton#StartBtn {
                background-color: #DBEAFE;
                color: #1E40AF;
                border-radius: 6px;
                font-weight: bold;
                font-size: 11px;
                padding: 5px 12px;
                border: 1px solid #BFDBFE;
            }
            QPushButton#StartBtn:hover { background-color: #BFDBFE; }

            QPushButton#FinishBtn {
                background-color: #D1FAE5;
                color: #065F46;
                border-radius: 6px;
                font-weight: bold;
                font-size: 11px;
                padding: 5px 12px;
                border: 1px solid #A7F3D0;
            }
            QPushButton#FinishBtn:hover { background-color: #A7F3D0; }

            /* Bouton Déconnexion (Style Login) */
            QPushButton#PrimaryAction {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4B5563, stop:1 #1F2937);
                color: white;
                border-radius: 10px;
                padding: 12px 24px;
                font-weight: bold;
                border: none;
            }
            QPushButton#PrimaryAction:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #6B7280, stop:1 #374151);
            }
        """)

    def init_ui(self):
        self.main_card = QFrame()
        self.main_card.setObjectName("MainCard")
        
        # Effet d'ombre sur la carte
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 15))
        shadow.setYOffset(10)
        self.main_card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(self.main_card)
        card_layout.setContentsMargins(35, 35, 35, 35)
        card_layout.setSpacing(25)

        # Header de la carte
        header_area = QHBoxLayout()
        title = QLabel("Tableau de Bord des Tâches")
        title.setObjectName("TitleLabel")
        header_area.addWidget(title)
        header_area.addStretch()
        
        card_layout.addLayout(header_area)

        # Configuration de la Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["TITRE", "DESCRIPTION", "PRIORITÉ", "DÉBUT", "ÉCHÉANCE", "STATUT", "ACTION"])
        
        # Comportement de la table
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents) # Titre s'adapte
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(60) # Lignes plus hautes
        self.table.setShowGrid(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        self.load_data()
        card_layout.addWidget(self.table)

        # Footer
        footer = QHBoxLayout()
        footer.addStretch()
        btn_logout = QPushButton("Déconnection")
        btn_logout.setObjectName("PrimaryAction")
        btn_logout.setCursor(Qt.PointingHandCursor)
        if self.logout_callback: 
            btn_logout.clicked.connect(self.logout_callback)
        footer.addWidget(btn_logout)
        card_layout.addLayout(footer)

        self.layout.addWidget(self.main_card)

    def load_data(self):
        endpoint = f"{BACKEND_URL}/tasks/user/{self.user_id}"
        try:
            resp = requests.get(endpoint, timeout=5)
            if resp.status_code == 200:
                tasks = resp.json()
                self.table.setRowCount(len(tasks))
                now = datetime.now()
                overdue_ids_to_sync = []

                for row, task in enumerate(tasks):
                    # Style des items texte
                    for col, key in enumerate(['title', 'description', 'priority', 'start_date', 'end_date']):
                        val = str(task.get(key, ''))
                        item = QTableWidgetItem(val)
                        item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                        if col == 0: # Titre en gras
                             item.setFont(QFont("Segoe UI", 10, QFont.Bold))
                        self.table.setItem(row, col, item)

                    # Gestion avancée du Statut avec Badges
                    backend_status = self.normalize_status(task.get('status', ''))
                    end_date_str = str(task.get('end_date', ''))
                    display_status = backend_status

                    # Logic Retard
                    end_date_dt = self.parse_end_date(end_date_str)
                    if end_date_dt and backend_status not in ["terminé", "en retard"] and now > end_date_dt:
                        display_status = "en retard"
                        if backend_status == "en cours":
                            task_id = task.get('id')
                            if task_id is not None:
                                overdue_ids_to_sync.append(task_id)

                    self.set_status_badge(row, display_status)
                    self.add_row_actions(row, task, display_status, backend_status)

                # Synchronise le statut backend des tâches en cours dépassées.
                if overdue_ids_to_sync and not self._is_syncing_overdue:
                    self._sync_overdue_tasks(overdue_ids_to_sync)
            else:
                self.table.setRowCount(0)
        except Exception as e:
            print(f"Erreur chargement tasks: {e}")

    def _sync_overdue_tasks(self, task_ids):
        self._is_syncing_overdue = True
        updated = False
        try:
            for task_id in task_ids:
                url = f"{BACKEND_URL}/tasks/{task_id}/status"
                try:
                    resp = requests.put(url, json={"new_status": "en retard"}, timeout=5)
                    if resp.status_code == 200:
                        updated = True
                except Exception:
                    # Évite de casser l'UI si une requête échoue.
                    continue
        finally:
            self._is_syncing_overdue = False

        if updated:
            self.load_data()

    def normalize_status(self, raw_status):
        status = str(raw_status or "").strip().lower().replace("_", " ")
        aliases = {
            "non commencé": "non commencé",
            "non commence": "non commencé",
            "not started": "non commencé",
            "en cours": "en cours",
            "in progress": "en cours",
            "terminé": "terminé",
            "termine": "terminé",
            "completed": "terminé",
            "en retard": "en retard",
            "late": "en retard",
            "overdue": "en retard",
        }
        return aliases.get(status, status)

    def parse_end_date(self, end_date_str):
        if not end_date_str:
            return None

        for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.strptime(end_date_str, fmt)
            except ValueError:
                continue

        try:
            iso_value = end_date_str.replace("Z", "+00:00")
            parsed = datetime.fromisoformat(iso_value)
            if parsed.tzinfo is not None:
                return parsed.replace(tzinfo=None)
            return parsed
        except ValueError:
            return None

    def set_status_badge(self, row, status):
        """ Crée un petit label stylisé pour le statut """
        badge = QLabel(status.upper())
        badge.setAlignment(Qt.AlignCenter)
        badge.setFixedWidth(100)
        
        # Styles de badges SaaS
        common_style = "font-weight: bold; font-size: 9px; border-radius: 12px; padding: 4px;"
        
        if status == "en retard":
            badge.setStyleSheet(f"{common_style} background-color: #FEE2E2; color: #991B1B;")
        elif status == "en cours":
            badge.setStyleSheet(f"{common_style} background-color: #E0E7FF; color: #3730A3;")
        elif status == "terminé":
            badge.setStyleSheet(f"{common_style} background-color: #D1FAE5; color: #065F46;")
        else: # Non commencé
            badge.setStyleSheet(f"{common_style} background-color: #F3F4F6; color: #374151;")

        container = QWidget()
        l = QHBoxLayout(container)
        l.addWidget(badge)
        l.setAlignment(Qt.AlignCenter)
        l.setContentsMargins(0,0,0,0)
        self.table.setCellWidget(row, 5, container)

    def add_row_actions(self, row, task, display_status, backend_status):
        task_id = task.get('id')
        effective_status = self.normalize_status(display_status)
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(10, 0, 10, 0)

        if effective_status == "terminé":
            lbl = QLabel("Complété")
            lbl.setStyleSheet("color: #10B981; font-weight: bold; font-size: 11px;")
            layout.addWidget(lbl)
            layout.setAlignment(Qt.AlignCenter)
        
        elif effective_status == "en retard":
            btn = QPushButton("Terminer")
            btn.setObjectName("FinishBtn")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _, b=btn, tid=task_id: self.handle_action_click(b, tid, "terminer"))
            layout.addWidget(btn)

        elif effective_status == "en cours":
            btn = QPushButton("Terminer")
            btn.setObjectName("FinishBtn")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _, b=btn, tid=task_id: self.handle_action_click(b, tid, "terminer"))
            layout.addWidget(btn)

        elif effective_status == "non commencé":
            btn = QPushButton("Démarrer")
            btn.setObjectName("StartBtn")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _, b=btn, tid=task_id: self.handle_action_click(b, tid, "commencer"))
            layout.addWidget(btn)

        else:
            # Fallback pour un statut inconnu: ne pas proposer "Démarrer" par erreur.
            btn = QPushButton("Terminer")
            btn.setObjectName("FinishBtn")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _, b=btn, tid=task_id: self.handle_action_click(b, tid, "terminer"))
            layout.addWidget(btn)

        self.table.setCellWidget(row, 6, container)

    def update_status(self, task_id, new_status):
        url = f"{BACKEND_URL}/tasks/{task_id}/status"
        try:
            resp = requests.put(url, json={"new_status": new_status}, timeout=5)
            if resp.status_code == 200:
                self.load_data()
            else:
                QMessageBox.warning(self, "Erreur", "Impossible de mettre à jour le statut.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur Connexion", str(e))

    def update_status_by_action(self, task_id, action):
        url = f"{BACKEND_URL}/tasks/{task_id}/action"
        try:
            resp = requests.put(url, json={"action": action}, timeout=5)
            if resp.status_code == 200:
                self.load_data()
            else:
                QMessageBox.warning(self, "Erreur", "Impossible de mettre à jour le statut.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur Connexion", str(e))

    def handle_action_click(self, button, task_id, action):
        # Bloque les doubles clics tant que la requête est en cours.
        button.setEnabled(False)
        self.update_status_by_action(task_id, action)