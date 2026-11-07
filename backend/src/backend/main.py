import os

import uvicorn
from dotenv import load_dotenv

from backend.app import create_app
from backend.config import Settings

load_dotenv()
settings = Settings.from_env(os.environ)
app = create_app(settings)


def main() -> None:
    uvicorn.run(app, host='0.0.0.0', port=settings.port)


if __name__ == '__main__':
    main()
