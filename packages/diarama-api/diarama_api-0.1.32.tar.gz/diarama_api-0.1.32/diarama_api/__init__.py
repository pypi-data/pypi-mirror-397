from diarama_api.shop import Shop
from .client import DiaramaAPIClient
from .auth import Auth
from .players import Players
from .games import Games
from .payments import Payments
from .media import Media
from .platforms import Platforms
from .files import Files
from .roles import Roles  # Добавлен

class DiaramaAPI:
    def __init__(self, api_key, base_url=None):
        self.client = DiaramaAPIClient(api_key, base_url) if base_url else DiaramaAPIClient(api_key)
        self.auth = Auth(self.client)
        self.players = Players(self.client)
        self.games = Games(self.client)
        self.payments = Payments(self.client)
        self.media = Media(self.client)
        self.platforms = Platforms(self.client)
        self.files = Files(self.client)
        self.shop = Shop(self.client)
        self.roles = Roles(self.client)  # Добавлен