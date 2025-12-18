class Payments:
    def __init__(self, client):
        self.client = client

    def list(self, player_id=None, status_id=None, from_date=None, to_date=None):
        params = {}
        if player_id:
            params["player_id"] = player_id
        if status_id:
            params["status_id"] = status_id
        if from_date:
            params["from_date"] = from_date
        if to_date:
            params["to_date"] = to_date
        return self.client._get("/payments/", params=params)

    def get(self, payment_id):
        return self.client._get(f"/payments/{payment_id}")

    def create(self, player_id, amount, status_id, currency="USD", 
               payment_method=None, user_game_id=None, shop_purchase_id=None):
        data = {
            "player_id": player_id,
            "amount": amount,
            "status_id": status_id,
            "currency": currency
        }
        if payment_method:
            data["payment_method"] = payment_method
        if user_game_id:
            data["user_game_id"] = user_game_id
        if shop_purchase_id:
            data["shop_purchase_id"] = shop_purchase_id
        return self.client._post("/payments/", data)

    def update_status(self, payment_id, status_id):
        return self.client._put(f"/payments/{payment_id}/status", {"status_id": status_id})

    def delete(self, payment_id):
        return self.client._delete(f"/payments/{payment_id}")

    def get_statuses(self):
        return self.client._get("/payments/statuses")

    def create_status(self, name, description=None):
        data = {"name": name}
        if description:
            data["description"] = description
        return self.client._post("/payments/statuses", data)

    def get_stats(self, from_date=None, to_date=None):
        params = {}
        if from_date:
            params["from_date"] = from_date
        if to_date:
            params["to_date"] = to_date
        return self.client._get("/payments/stats", params=params)