import requests
import json
import webbrowser

class MicrosoftAuth:
    def __init__(self, client_id: str):
        self.client_id = client_id
        self.redirect_uri = "https://login.live.com/oauth20_desktop.srf"
        self.scope = "XboxLive.signin offline_access"

    def get_auth_url(self):
        return f"https://login.live.com/oauth20_authorize.srf?client_id={self.client_id}&response_type=code&redirect_uri={self.redirect_uri}&scope={self.scope}"

    def exchange_code(self, code: str):
        data = {
            "client_id": self.client_id,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri
        }
        r = requests.post("https://login.live.com/oauth20_token.srf", data=data)
        r.raise_for_status()
        return r.json()  # access_token, refresh_token

    def xbox_auth(self, access_token: str):
        """Получаем XSTS token для Minecraft"""
        payload = {
            "Properties": {
                "AuthMethod": "RPS",
                "SiteName": "user.auth.xboxlive.com",
                "RpsTicket": f"d={access_token}"
            },
            "RelyingParty": "rp://api.minecraftservices.com/",
            "TokenType": "JWT"
        }
        r = requests.post("https://user.auth.xboxlive.com/user/authenticate", json=payload)
        r.raise_for_status()
        return r.json()

    def get_mc_token(self, xsts_token: dict):
        """Получаем токен Minecraft"""
        payload = {
            "identityToken": f"XBL3.0 x={xsts_token['DisplayClaims']['xui'][0]['uhs']};{xsts_token['Token']}"
        }
        r = requests.post("https://api.minecraftservices.com/authentication/login_with_xbox", json=payload)
        r.raise_for_status()
        return r.json()  # access_token для игры
