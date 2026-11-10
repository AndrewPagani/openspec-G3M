import os

import reflex as rx

config = rx.Config(
    app_name="app",
    api_url=os.getenv("REFLEX_API_URL", "http://127.0.0.1:8001"),
)
