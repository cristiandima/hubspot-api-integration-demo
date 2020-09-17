import os

SECRET_KEY = os.getenv("SECRET_KEY", "bn6r7YAAnLT52NsT9DxbMt3k")

HUB_CLIENT_ID = os.getenv("HUB_CLIENT_ID", "fc7e2ddb-38e2-4753-8788-c150a7e8128e")
HUB_CLIENT_SECRET = os.getenv(
    "HUB_CLIENT_SECRET", "13a7c01d-4c5b-4c2f-998e-7bec93860e33"
)
HUB_REDIRECT_URI = os.getenv("HUB_REDIRECT_URI", "http://localhost:3000/auth/hubapi")
HUB_REFRESH_URI = os.getenv("HUB_REFRESH_URI", "https://api.hubapi.com/oauth/v1/token")

DEALS_BASE_URL = "https://api.hubapi.com/crm/v3/objects/deals"
