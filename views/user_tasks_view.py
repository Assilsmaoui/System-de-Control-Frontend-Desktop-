import requests
from config.settings import BACKEND_URL
from datetime import datetime
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, 
                             QTableWidgetItem, QPushButton, QHeaderView, QFrame, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor

class UserTasksViewQt(QWidget):
    def __init__(self, user_id, logout_callback=None, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.logout_callback = logout_callback
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.apply_styles()
        self.init_ui()

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget { background-color: transparent; }
            QFrame#MainCard {
                background-color: #FFFFFF;
                border-radius: 20px;
                border: 1px solid #E5E7EB;
            }
            QLabel#TitleLabel {
                font-size: 26px; font-weight: 800; color: #111827; letter-spacing: -1px;
            }
            QTableWidget {
                background-color: transparent; border: none;
                gridline-color: #F3F4F6; font-size: 14px; color: #374151;
            }
            QHeaderView::section {
                background-color: #F9FAFB; padding: 12px; border: none;
                border-bottom: 2px solid #E5E7EB; font-weight: bold;
                color: #6B7280; text-transform: uppercase;
            }
            /* Boutons d'action */
            QPushButton#StartBtn {
                background-color: #3B82F6; color: white; border-radius: 8px;
                font-weight: bold; padding: 6px; border: none;
            }
            QPushButton#FinishBtn {
                background-color: #10B981; color: white; border-radius: 8px;
                font-weight: bold; padding: 6px; border: none;
            }
            QPushButton#PrimaryAction {
                background-color: #1F2937; color: white; border-radius: 12px;
                padding: 12px 24px; font-weight: bold; border: none;
            }
        """)

    def init_ui(self):
        self.main_card = QFrame()
        self.main_card.setObjectName("MainCard")
        card_layout = QVBoxLayout(self.main_card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(20)

        # Header
        title = QLabel("Tableau de Bord des Tâches")
        title.setObjectName("TitleLabel")
        card_layout.addWidget(title)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["Titre", "Description", "Priorité", "Début", "Fin", "Statut", "Action"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        self.load_data()
        card_layout.addWidget(self.table)

        # Footer (Déconnecter)
        footer = QHBoxLayout()
        footer.addStretch()
        btn_logout = QPushButton("Déconnecter")
        btn_logout.setObjectName("PrimaryAction")
        btn_logout.setFixedWidth(180)
        if self.logout_callback: btn_logout.clicked.connect(self.logout_callback)
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

                for row, task in enumerate(tasks):
                    self.table.setItem(row, 0, QTableWidgetItem(task.get('title', '')))
                    self.table.setItem(row, 1, QTableWidgetItem(task.get('description', '')))
                    self.table.setItem(row, 2, QTableWidgetItem(str(task.get('priority', ''))))

                    end_date_str = task.get('end_date', '')
                    self.table.setItem(row, 3, QTableWidgetItem(task.get('start_date', '')))
                    self.table.setItem(row, 4, QTableWidgetItem(end_date_str))

                    # Statut réel du backend
                    backend_status = task.get('status', '').lower()
                    status = backend_status

                    # Vérification du retard (affichage seulement, le backend reste prioritaire)
                    try:
                        end_date_dt = datetime.strptime(end_date_str, "%Y-%m-%d")
                        if backend_status not in ["terminé", "en retard"] and now > end_date_dt:
                            status = "en retard"
                    except Exception:
                        pass

                    status_item = QTableWidgetItem(status.upper())
                    status_item.setTextAlignment(Qt.AlignCenter)
                    status_item.setFont(QFont("Segoe UI", 9, QFont.Bold))

                    if status == "en retard":
                        status_item.setForeground(QColor("#EF4444"))
                    elif status == "en cours":
                        status_item.setForeground(QColor("#3B82F6"))
                    elif status == "terminé":
                        status_item.setForeground(QColor("#10B981"))
                    else:
                        status_item.setForeground(QColor("#6B7280"))

                    self.table.setItem(row, 5, status_item)
                    self.add_row_actions(row, task, status, backend_status)
            else:
                self.table.setRowCount(0)
        except Exception:
            pass

    def add_row_actions(self, row, task, display_status, backend_status=None):
        task_id = task.get('id')
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(5, 2, 5, 2)

        # Si la tâche est terminée côté backend
        if backend_status == "terminé":
            layout.addWidget(QLabel("✅ Terminé"))
        # Si la tâche n'est pas commencée
        elif backend_status == "non commencé":
            btn = QPushButton("Démarrer")
            btn.setObjectName("StartBtn")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda: self.update_status(task_id, "en cours"))
            layout.addWidget(btn)
        # Si la tâche est en cours ou en retard (affichage)
        elif backend_status == "en cours" or display_status == "en retard":
            btn = QPushButton("Terminer")
            btn.setObjectName("FinishBtn")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda: self.update_status(task_id, "terminé"))
            layout.addWidget(btn)
        else:
            layout.addWidget(QLabel("-"))

        self.table.setCellWidget(row, 6, container)

    def update_status(self, task_id, new_status):
        """ Envoie la mise à jour au backend """
        url = f"{BACKEND_URL}/tasks/{task_id}/status"
        try:
            resp = requests.put(url, json={"new_status": new_status}, timeout=5)
            if resp.status_code == 200:
                self.load_data()
            else:
                try:
                    error_msg = resp.json().get("detail") or resp.text
                except Exception:
                    error_msg = resp.text
                print(f"Erreur backend (update_status): {error_msg}")
                QMessageBox.critical(self, "Erreur", f"Le serveur n'a pas pu mettre à jour la tâche.\n{error_msg}")
        except Exception as e:
            print(f"Erreur connexion (update_status): {e}")
            QMessageBox.critical(self, "Erreur", f"Connexion impossible au serveur.\n{e}")