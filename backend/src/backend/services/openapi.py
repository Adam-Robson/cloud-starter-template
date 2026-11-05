import json
import sys

from backend.app import create_app
from backend.config import Settings


def main() -> None:
    '''Print the OpenAPI schema; the frontend generates its types from it.'''
    app = create_app(Settings.from_env({}))
    json.dump(app.openapi(), sys.stdout, indent=2)
    sys.stdout.write('\n')
