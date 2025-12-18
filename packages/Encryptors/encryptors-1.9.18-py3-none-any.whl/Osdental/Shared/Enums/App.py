import os
from enum import StrEnum
from dotenv import load_dotenv

load_dotenv(dotenv_path='.env', override=True)

class App(StrEnum):
    LEGACY_NAME = os.getenv('LEGACY_NAME')
    MICROSERVICE_NAME = os.getenv('MICROSERVICE_NAME')
    JWT_USER_KEY = os.getenv('JWT_USER_KEY')
    ENVIRONMENT = os.getenv('ENVIRONMENT')
    MICROSERVICE_VERSION = os.getenv('MICROSERVICE_VERSION')