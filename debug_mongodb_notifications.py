from services.notification_service import NotificationService

user_id = "69b01374cd72ceb086fcb327"  # Remplace par l'id de test
notifications = NotificationService.get_notifications_by_user(user_id)
print("Notifications MongoDB:")
for notif in notifications:
    print(notif.to_dict())
if not notifications:
    print("Aucune notification trouvée.")
