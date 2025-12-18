class Players:
    def __init__(self, client):
        self.client = client

    def list(self):
        return self.client._get("/players/")

    def get(self, identifier):
        return self.client._get(f"/players/{identifier}")

    def create(self, username, password, email, role_id=None, avatar_id=None):
        data = {"username": username, "password": password, "email": email}
        if role_id:
            data["role_id"] = role_id
        if avatar_id:
            data["avatar_id"] = avatar_id
        return self.client._post("/players/", data)

    def login(self, username, password):
        data = {"username": username, "password": password}
        return self.client._post("/players/login", data)

    def update(self, identifier, **kwargs):
        allowed = ["email", "banned", "ban_reason", "role_id", "avatar_id", "password"]
        data = {k: v for k, v in kwargs.items() if k in allowed}
        return self.client._put(f"/players/{identifier}", data)

    def delete(self, identifier):
        return self.client._delete(f"/players/{identifier}")

    def get_stats(self, identifier):
        return self.client._get(f"/players/{identifier}/stats")

    def update_playtime(self, identifier, game_id, hours):
        data = {"game_id": game_id, "hours": hours}
        return self.client._post(f"/players/{identifier}/update-playtime", data)

    def get_games(self, identifier):
        return self.client._get(f"/players/{identifier}/games")