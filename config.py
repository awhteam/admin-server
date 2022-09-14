import os
import pyrogram
from gql import Client
from gql.transport.aiohttp import AIOHTTPTransport
from github import Github
import pymongo
from dotenv import load_dotenv
load_dotenv()


class Config(object):
    SECRET_KEY = os.getenv('SECRET_KEY')
    MAL_CLIENT_ID = os.getenv('MAL_CLIENT_ID')
    DATABASE_URL = os.getenv('DATABASE_URL')
    HEROKU_APP = None
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    APP_ID = int(os.getenv('APP_ID'))
    API_HASH = os.getenv('API_HASH')
    PORT = int(os.getenv('PORT', 5000))
    DOWNLOAD_LOCATION = "./DOWNLOADS"
    MAX_FILE_SIZE = 50000000
    TG_MAX_FILE_SIZE = 2097152000
    FREE_USER_MAX_FILE_SIZE = 50000000
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 128))
    LOGGER_GP = int(os.getenv('LOGGER_GP'))
    UPDATES_CHANNEL = -1001609755558
    bot = pyrogram.Client(
        "AW",
        bot_token=BOT_TOKEN,
        api_id=APP_ID,
        api_hash=API_HASH,
        plugins=dict(root="plugins")
    )

    vnc_mod_bot = pyrogram.Client(
        "vnc",
        bot_token="5281302075:AA_BOT_TOKEN_ERqQ8tGM",
        api_id=APP_ID,
        api_hash=API_HASH,
        plugins=dict(root="vnc_mod")
    )

    sxf_mod_bot = pyrogram.Client(
        "SxF",
        bot_token="5281302075:AA_BOT_TOKEN_ERqQ8tGM",
        api_id=APP_ID,
        api_hash=API_HASH,
        plugins=dict(root="SxF_mod")
    )
    ANILIST_CLIENT = Client(transport=AIOHTTPTransport(
        url="https://graphql.anilist.co"), fetch_schema_from_transport=True)
    GITHUB_MEDIA = Github(os.getenv('GH_MEDIA_TOKEN')).get_repo(
        "awhteam/AW_DL-Media")
    SEARCH_DB = pymongo.MongoClient(
        os.getenv('SEARCH_DB'), maxPoolSize=100).get_database().search
