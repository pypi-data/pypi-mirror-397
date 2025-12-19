import requests
from requests_oauth2client import OAuth2Client, OAuth2ClientCredentialsAuth

from .options import Options

class API:
    def __init__(self, options: Options):
        self.api_base_url = options.api_base_url
        self.api_key = options.api_key
        self.token_url = options.oauth_token_url
        self.client_id = options.oauth_client_id
        self.client_secret = options.oauth_client_secret
        self.user_context = options.user_context
        self.session = None

    def _authenticate(self):
        if self.session:
            return self.session

        # Configure OAuth2 client with automatic token fetching
        oauth2_client = OAuth2Client(
            token_endpoint=self.token_url,
            client_id=self.client_id,
            client_secret=self.client_secret
        )
        
        # Create an auth object that handles token fetching and refreshing
        auth = OAuth2ClientCredentialsAuth(oauth2_client)

        # Create a standard requests session and attach the auth handler
        self.session = requests.Session()
        self.session.auth = auth
        
        return self.session

    def invoke(self, method: str, endpoint: str, payload: dict | None = None) -> dict:
        session = self._authenticate()
        
        api_url = f"{self.api_base_url}/{endpoint.lstrip('/')}"
        
        headers = {
            "X-Api-Key": self.api_key,
            "X-User-Context": self.user_context,
            "Content-Type": "application/json"
        }
        
        response = session.request(method=method, url=api_url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
