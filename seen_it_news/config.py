import os

from grift import BaseConfig, ConfigProperty, JsonFileLoader
from schematics.types import StringType


HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(HERE, '.config.json')

class AppConfig(BaseConfig):
    MC_API_KEY = ConfigProperty(property_type=StringType(), required=True)
    access_token = ConfigProperty(property_type=StringType(), required=True)
    access_token_secret = ConfigProperty(property_type=StringType(), required=True)
    consumer_key = ConfigProperty(property_type=StringType(), required=True)
    consumer_secret = ConfigProperty(property_type=StringType(), required=True)
    DB_FILE = ConfigProperty(property_type=StringType(), default=os.path.join(HERE, 'history.db'))

app_config = AppConfig([JsonFileLoader(CONFIG_PATH)])
