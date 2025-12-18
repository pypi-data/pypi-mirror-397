class Media:
    def __init__(self, client):
        self.client = client

    def upload_image(self, file_obj, image_type='screenshot', alt_text=None):
        """Загрузить изображение"""
        if hasattr(file_obj, "filename"):
            filename = file_obj.filename
        else:
            filename = "image.jpg"
        
        files = {'file': (filename, file_obj)}
        data = {'type': image_type}
        if alt_text:
            data['alt_text'] = alt_text
        
        return self.client._post("/media/images/upload", data=data, files=files)

    def get_images(self, image_type=None):
        params = {}
        if image_type:
            params['type'] = image_type
        return self.client._get("/media/images", params=params)

    def delete_image(self, image_id):
        return self.client._delete(f"/media/images/{image_id}")

    def create_collection(self, avatar_id=None, banner_id=None, icon_id=None, screenshots=None):
        data = {}
        if avatar_id:
            data["avatar_id"] = avatar_id
        if banner_id:
            data["banner_id"] = banner_id
        if icon_id:
            data["icon_id"] = icon_id
        if screenshots:
            data["screenshots"] = screenshots
        return self.client._post("/media/collections", data)

    def get_collection(self, media_id):
        return self.client._get(f"/media/collections/{media_id}")

    def update_collection(self, media_id, **data):
        return self.client._put(f"/media/collections/{media_id}", data)

    def delete_collection(self, media_id):
        return self.client._delete(f"/media/collections/{media_id}")

    def quick_create(self, avatar=None, banner=None, icon=None, screenshots=None):
        """Быстрое создание медиа-коллекции с файлами"""
        files = {}
        if avatar:
            files['avatar'] = avatar
        if banner:
            files['banner'] = banner
        if icon:
            files['icon'] = icon
        if screenshots:
            if isinstance(screenshots, list):
                for i, screenshot in enumerate(screenshots):
                    files[f'screenshots'] = screenshot
            else:
                files['screenshots'] = screenshots
        
        return self.client._post("/media/quick-create", files=files)