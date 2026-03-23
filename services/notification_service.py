import requests
from models.notification import Notification

class NotificationService:
    BASE_URL = "http://localhost:8000/notifications"

    @staticmethod
    def get_notifications_by_user(user_id):
        endpoint = f"{NotificationService.BASE_URL}/{user_id}"
        try:
            resp = requests.get(endpoint)
            if resp.status_code == 200:
                notifications_data = resp.json()
                return [Notification.from_dict(n) for n in notifications_data]
            else:
                return []
        except Exception:
            return []
