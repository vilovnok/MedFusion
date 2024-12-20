from dotenv import load_dotenv
import os

load_dotenv()

# auth
SECRET = os.environ.get('SECRET')
REFRESH_SECRET = os.environ.get('REFRESH_SECRET')
ALGORITHM = os.environ.get('ALGORITHM')

# postgres
DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASS = os.environ.get('DB_PASS')