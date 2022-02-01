import os
import pyrogram


class Config(object):
    os.environ['BOT_TOKEN']="***REMOVED***"
    os.environ['APP_ID']="***REMOVED***"
    os.environ['API_HASH']="***REMOVED***"
    os.environ['LOGGER_GP']="-486977904"
    os.environ['MAL_CLIENT_ID']="***REMOVED***"
    os.environ['DATABASE_URL']='***REMOVED***'
    MAL_CLIENT_ID = os.environ.get('MAL_CLIENT_ID')
    DATABASE_URL = os.environ.get('DATABASE_URL')
    HEROKU_APP=None
    BOT_TOKEN = os.environ.get('BOT_TOKEN')
    APP_ID = int(os.environ.get('APP_ID'))
    API_HASH = os.environ.get('API_HASH')
    PORT = int(os.environ.get('PORT',5000))
    DOWNLOAD_LOCATION = "./DOWNLOADS"
    MAX_FILE_SIZE = 50000000
    TG_MAX_FILE_SIZE = 2097152000
    FREE_USER_MAX_FILE_SIZE = 50000000
    CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE", 128))
    LOGGER_GP = int(os.environ.get('LOGGER_GP'))
    UPDATES_CHANNEL=-1001609755558
    bot = pyrogram.Client(
        "AW",
        bot_token=BOT_TOKEN,
        api_id=APP_ID,
        api_hash=API_HASH,
        plugins=dict(root="plugins")
    )