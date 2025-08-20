import os
from authlib.integrations.starlette_client import OAuth
from dotenv import load_dotenv

load_dotenv()

oauth = OAuth()

# Google
oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    access_token_url="https://oauth2.googleapis.com/token",
    client_kwargs={"scope": "openid email profile"},
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
)

# Facebook
oauth.register(
    name="facebook",
    client_id=os.getenv("FACEBOOK_CLIENT_ID"),
    client_secret=os.getenv("FACEBOOK_CLIENT_SECRET"),
    authorize_url="https://www.facebook.com/v14.0/dialog/oauth",
    access_token_url="https://graph.facebook.com/v14.0/oauth/access_token",
    api_base_url="https://graph.facebook.com/v14.0/",
    client_kwargs={"scope": "email"},
)
