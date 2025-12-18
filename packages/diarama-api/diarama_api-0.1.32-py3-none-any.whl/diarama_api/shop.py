class Shop:
    def __init__(self, client):
        self.client = client

    # Категории
    def get_categories(self):
        return self.client._get("/shop/categories")

    def create_category(self, name, description=None, icon_id=None):
        data = {"name": name}
        if description:
            data["description"] = description
        if icon_id:
            data["icon_id"] = icon_id
        return self.client._post("/shop/categories", data)

    def update_category(self, category_id, **data):
        return self.client._put(f"/shop/categories/{category_id}", data)

    def delete_category(self, category_id):
        return self.client._delete(f"/shop/categories/{category_id}")

    # Типы товаров
    def get_product_types(self):
        return self.client._get("/shop/product-types")

    def create_product_type(self, name, description=None, requires_license_key=False, allow_multiple_purchase=False):
        data = {
            "name": name,
            "requires_license_key": requires_license_key,
            "allow_multiple_purchase": allow_multiple_purchase
        }
        if description:
            data["description"] = description
        return self.client._post("/shop/product-types", data)

    # Товары
    def get_products(self, category_id=None, type_id=None, is_active=None):
        params = {}
        if category_id:
            params["category_id"] = category_id
        if type_id:
            params["type_id"] = type_id
        if is_active is not None:
            params["is_active"] = str(is_active).lower()
        return self.client._get("/shop/products", params=params)

    def get_product(self, product_id):
        return self.client._get(f"/shop/products/{product_id}")

    def create_product(self, **data):
        return self.client._post("/shop/products", data)

    def update_product(self, product_id, **data):
        return self.client._put(f"/shop/products/{product_id}", data)

    def delete_product(self, product_id):
        return self.client._delete(f"/shop/products/{product_id}")

    # Покупки
    def get_purchases(self, player_id=None):
        params = {}
        if player_id:
            params["player_id"] = player_id
        return self.client._get("/shop/purchases", params=params)

    def create_purchase(self, player_id, product_id):
        data = {"player_id": player_id, "product_id": product_id}
        return self.client._post("/shop/purchases", data)

    def delete_purchase(self, purchase_id):
        return self.client._delete(f"/shop/purchases/{purchase_id}")