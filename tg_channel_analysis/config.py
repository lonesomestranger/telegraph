import configparser
import os

config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(__file__), '..', 'config.ini')

if not os.path.exists(config_path):
    raise FileNotFoundError(
        "Файл конфигурации 'config.ini' не найден. "
        "Скопируйте 'config.ini.example' в 'config.ini' и заполните его."
    )

config.read(config_path)

API_ID = config.getint('pyrogram', 'api_id')
API_HASH = config.get('pyrogram', 'api_hash')
PHONE_NUMBER = config.get('pyrogram', 'phone_number')

SCAN_LIMIT = config.getint('scanner', 'scan_limit', fallback=200)
MAX_DEPTH = config.getint('scanner', 'max_depth', fallback=3)
CHANNEL_SCAN_PAUSE = config.getint('scanner', 'channel_scan_pause', fallback=5)
MESSAGE_BATCH_PAUSE = config.getint('scanner', 'message_batch_pause', fallback=2)
MESSAGE_BATCH_SIZE = config.getint('scanner', 'message_batch_size', fallback=50)