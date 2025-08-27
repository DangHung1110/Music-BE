import os
from dotenv import load_dotenv
load_dotenv()
class JamendoConfig:
    JAMENDO_CLIENT_ID=os.getenv("JAMENDO_CLIENT_ID")
    BASE_URL="https://api.jamendo.com/v3.0"