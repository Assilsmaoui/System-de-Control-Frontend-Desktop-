import threading
import websocket
import json
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QScrollArea, 
                             QFrame, QPushButton, QHBoxLayout, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QFont

# --- COMPOSANT 1 : LA CARTE INDIVIDUELLE ---
class NotificationCard(QFrame):
    """Une bulle de notification stylisée, cliquable pour marquer comme lue"""
    def __init__(self, notif, on_read_callback=None):
        super().__init__()
        self.notif = notif
        self.on_read_callback = on_read_callback
        self.setFixedHeight(85)
        self.setStyleSheet("""
            QFrame {
                background-color: #F9FAFB;
                border: 1px solid #E5E7EB;
                border-radius: 12px;
                margin: 4px;
            }
            QFrame:hover {
                background-color: #F3F4F6;
                border: 1px solid #D1D5DB;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        msg_label = QLabel(getattr(notif, 'message', str(notif)))
        msg_label.setWordWrap(True)
        msg_label.setStyleSheet("color: #1F2937; font-size: 13px; font-weight: 500; border: none; background: transparent;")

        time_label = QLabel(getattr(notif, 'created_at', "À l'instant"))
        time_label.setStyleSheet("color: #9CA3AF; font-size: 11px; border: none; background: transparent;")

        layout.addWidget(msg_label)
        layout.addWidget(time_label, alignment=Qt.AlignRight)

        # Si non lu, surbrillance
        if hasattr(notif, 'is_read') and not notif.is_read:
            self.setStyleSheet(self.styleSheet() + "QFrame { border: 2px solid #EF4444; }")

    def mousePressEvent(self, event):
        # Si notification non lue, marquer comme lue
        if hasattr(self.notif, 'is_read') and not self.notif.is_read:
            import requests
            try:
                requests.put(f"http://localhost:8000/notifications/mark_read/{self.notif.id}", timeout=5)
            except Exception:
                pass
            if self.on_read_callback:
                self.on_read_callback()
        super().mousePressEvent(event)

# --- COMPOSANT 2 : LA FENÊTRE FLOTTANTE ---
class NotificationFlyout(QFrame):
    """Le menu qui apparaît sous la cloche"""
    def __init__(self, parent=None):
        super().__init__(parent, Qt.ToolTip | Qt.FramelessWindowHint)
        self.setFixedWidth(320)
        self.setFixedHeight(400)
        self.setObjectName("NotifWindow")
        
        self.setStyleSheet("""
            QFrame#NotifWindow {
                background-color: #FFFFFF;
                border: 1px solid #E5E7EB;
                border-radius: 16px;
            }
            QLabel#HeaderTitle {
                font-weight: 800;
                color: #111827;
                font-size: 17px;
                padding: 15px;
            }
            QScrollArea { border: none; background: transparent; }
        """)

        # Ombre portée pour l'effet de profondeur
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setXOffset(0)
        shadow.setYOffset(12)
        shadow.setColor(QColor(0, 0, 0, 45))
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 10)
        
        # Titre
        header = QLabel("Notifications")
        header.setObjectName("HeaderTitle")
        layout.addWidget(header)

        # Zone de défilement
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setAlignment(Qt.AlignTop)
        self.container_layout.setSpacing(5)
        self.scroll.setWidget(self.container)
        layout.addWidget(self.scroll)

    def clear_list(self):
        while self.container_layout.count():
            child = self.container_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

# --- COMPOSANT 3 : LE MANAGER ---
class NotificationManager:
    def __init__(self, parent, user_id, badge_label, notification_icon_button, update_tasks_callback=None):
        self.parent = parent
        self.user_id = user_id
        self.badge_label = badge_label
        self.icon_button = notification_icon_button
        self.notifications = []
        self.update_tasks_callback = update_tasks_callback
        self.ws_thread = None

        # Création de la fenêtre flottante
        self.flyout = NotificationFlyout(self.parent)
        self.flyout.hide()

        # Afficher le badge dès l'ouverture de l'application
        self.update_notification_badge()

        # Astuce : pour bien positionner le badge sur l'icône, utilise un QStackedLayout ou place badge_label en overlay sur notification_icon_button dans ta fenêtre principale.

    def start_notification_ws(self):
        def ws_run():
            ws_url = f"ws://localhost:8080/ws/notifications/{self.user_id}"
            def on_message(ws, message):
                notif = json.loads(message)
                self.notifications.append(notif)
                
                # Mise à jour badge
                self.update_notification_badge()
                
                # Mise à jour dynamique de la liste si elle est ouverte
                self.flyout.container_layout.insertWidget(0, NotificationCard(notif.get('message', 'Nouvelle tâche assignée')))
                
                if self.update_tasks_callback:
                    self.update_tasks_callback()

            ws = websocket.WebSocketApp(ws_url, on_message=on_message)
            ws.run_forever()

        self.ws_thread = threading.Thread(target=ws_run, daemon=True)
        self.ws_thread.start()

    def update_notification_badge(self):
        # Appel API pour récupérer le nombre de notifications non lues
        import requests
        try:
            url = f"http://localhost:8000/notifications/unread_count/{self.user_id}"
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                unread_count = resp.json().get("unread_count", 0)
            else:
                unread_count = 0
        except Exception:
            unread_count = 0
        if unread_count > 0:
            self.badge_label.setText(str(unread_count))
            self.badge_label.setVisible(True)
            self.badge_label.setStyleSheet("""
                background-color: #EF4444; 
                color: white; 
                border-radius: 9px; 
                font-size: 10px; 
                font-weight: bold;
                padding: 2px;
            """)
        else:
            self.badge_label.setVisible(False)

    def on_notification_clicked(self):
        """Ouvre/Ferme le menu flottant sous la cloche"""
        if self.flyout.isVisible():
            self.flyout.hide()
        else:
            # Recharger l'historique depuis le service
            from services.notification_service import NotificationService
            hist_notifs = NotificationService.get_notifications_by_user(self.user_id)

            self.flyout.clear_list()
            if hist_notifs:
                for n in hist_notifs:
                    self.flyout.container_layout.addWidget(
                        NotificationCard(n, on_read_callback=self.update_notification_badge)
                    )
            else:
                empty = QLabel("Aucune notification")
                empty.setStyleSheet("color: #9CA3AF; padding: 20px;")
                empty.setAlignment(Qt.AlignCenter)
                self.flyout.container_layout.addWidget(empty)

            # Positionnement précis sous le bouton cloche
            global_pos = self.icon_button.mapToGlobal(self.icon_button.rect().bottomLeft())
            self.flyout.move(global_pos.x() - 280, global_pos.y() + 12)
            self.flyout.show()
            self.flyout.raise_()