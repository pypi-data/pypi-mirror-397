from app import create_app
from dotenv import load_dotenv
import os

load_dotenv(override=True)

config = os.getenv("FLASK_ENV")
app = create_app(config)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT")))
