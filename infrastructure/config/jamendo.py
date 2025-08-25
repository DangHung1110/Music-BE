import os
from dotenv import load_dotenv
load_dotenv()
class JamendoConfig:
    CLIENT_ID=os.getenv("JAMENDO_CLIENT_ID")
    BASE_URL="https://api.jamendo.com/v3.0"