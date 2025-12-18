class OfflineAuth:
    def __init__(self, username="Steve"):
        self.username = username

    def get_args(self):
        return {
            "auth_player_name": self.username,
            "auth_uuid": "0"*32,
            "auth_access_token": "offline"
        }
