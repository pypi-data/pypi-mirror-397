class Roles:
    def __init__(self, client):
        self.client = client

    def list(self):
        return self.client._get("/roles/")

    def get(self, role_id):
        return self.client._get(f"/roles/{role_id}")

    def create(self, name, description=None, permissions=None):
        data = {"name": name}
        if description:
            data["description"] = description
        if permissions:
            data["permissions"] = permissions
        return self.client._post("/roles/", data)

    def update(self, role_id, **data):
        return self.client._put(f"/roles/{role_id}", data)

    def delete(self, role_id):
        return self.client._delete(f"/roles/{role_id}")