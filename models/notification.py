class Notification:
    def __init__(self, user_id, message, created_at=None, notif_id=None):
        self.user_id = user_id
        self.message = message
        self.created_at = created_at
        self.id = notif_id

    @classmethod
    def from_dict(cls, data):
        return cls(
            user_id=data.get('user_id'),
            message=data.get('message'),
            created_at=data.get('created_at'),
            notif_id=data.get('id')
        )

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'message': self.message,
            'created_at': self.created_at,
            'id': self.id
        }
