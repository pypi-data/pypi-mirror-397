import os
import argparse
from dataclasses import dataclass

@dataclass
class Options:
    api_base_url: str
    api_key: str
    oauth_token_url: str
    oauth_client_id: str
    oauth_client_secret: str
    user_context: str

    @staticmethod
    def from_env_and_args() -> 'Options':
        parser = argparse.ArgumentParser(description="Search API Client", add_help=False)
        parser.add_argument("--api-base-url", help="API Base URL")
        parser.add_argument("--api-key", help="API Key")
        parser.add_argument("--oauth-token-url", help="OAuth Token URL")
        parser.add_argument("--oauth-client-id", help="OAuth Client ID")
        parser.add_argument("--oauth-client-secret", help="OAuth Client Secret")
        parser.add_argument("--user-context", help="User Context")
        args, _ = parser.parse_known_args()

        missing_vars = []

        api_base_url = args.api_base_url or os.environ.get("API_BASE_URL")
        if not api_base_url: missing_vars.append("API_BASE_URL")

        api_key = args.api_key or os.environ.get("API_KEY")
        if not api_key: missing_vars.append("API_KEY")

        token_url = args.oauth_token_url or os.environ.get("OAUTH_TOKEN_URL")
        if not token_url: missing_vars.append("OAUTH_TOKEN_URL")
        
        client_id = args.oauth_client_id or os.environ.get("OAUTH_CLIENT_ID")
        if not client_id: missing_vars.append("OAUTH_CLIENT_ID")

        client_secret = args.oauth_client_secret or os.environ.get("OAUTH_CLIENT_SECRET")
        if not client_secret: missing_vars.append("OAUTH_CLIENT_SECRET")
        
        user_context = args.user_context or os.environ.get("USER_CONTEXT")
        if not user_context: missing_vars.append("USER_CONTEXT")

        if missing_vars:
            raise ValueError(f"Missing configuration (env vars or args): {', '.join(missing_vars)}")

        return Options(
            api_base_url=api_base_url,
            api_key=api_key,
            oauth_token_url=token_url,
            oauth_client_id=client_id,
            oauth_client_secret=client_secret,
            user_context=user_context
        )
