class Games:
    def __init__(self, client):
        self.client = client

    def list(self):
        return self.client._get("/games/")

    def get(self, game_id):
        return self.client._get(f"/games/{game_id}")

    def create(self, **data):
        return self.client._post("/games/", data)

    def update(self, game_id, **data):
        return self.client._put(f"/games/{game_id}", data)

    def delete(self, game_id):
        return self.client._delete(f"/games/{game_id}")

    def add_platform(self, game_id, platform_id, price=None, keys=None, is_available=True):
        data = {"platform_id": platform_id}
        if price is not None:
            data["price"] = price
        if keys is not None:
            data["keys"] = keys
        data["is_available"] = is_available
        return self.client._post(f"/games/{game_id}/platforms", data)

    def update_platform(self, game_platform_id, **data):
        return self.client._put(f"/games/platforms/{game_platform_id}", data)

    def remove_platform(self, game_platform_id):
        return self.client._delete(f"/games/platforms/{game_platform_id}")

    def get_keys(self, game_platform_id):
        return self.client._get(f"/games/platforms/{game_platform_id}/keys")

    def add_keys(self, game_platform_id, keys=None, count=None):
        data = {}
        if keys is not None:
            data["keys"] = keys
        if count is not None:
            data["count"] = count
        return self.client._post(f"/games/platforms/{game_platform_id}/keys", data)

    def delete_key(self, key_id):
        return self.client._delete(f"/games/keys/{key_id}")

    def grant_to_player(self, player_id, game_id, platform_id):
        data = {
            "player_id": player_id,
            "game_id": game_id,
            "platform_id": platform_id
        }
        return self.client._post("/games/grant", data)