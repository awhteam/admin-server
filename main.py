from config import Config
import threading
from flask import Flask, Response, _app_ctx_stack,request
from flask_cors import CORS
from pyrogram import idle
from database import models
from database.database import SessionLocal, engine, Base
from sqlalchemy.orm import scoped_session
import json
from services.anime import fetch_data_anilist,add_to_database
import requests
from datetime import datetime
from database.models import AnimeV2


app = Flask(__name__)
models.Base.metadata.create_all(bind=engine)
CORS(app)
app.session = scoped_session(
    SessionLocal, scopefunc=_app_ctx_stack.__ident_func__)
Base.query = app.session.query_property()



@app.route('/', methods=['GET', 'POST'])
def wake():
	return Response('ok', status=200)


@app.route('/anime/add', methods=['POST'])
def add_new_anime():
    data=json.loads(request.data)
    anilist_id=data['anilist_id']
    tg_post_id=data['tg_post_id']
    synopsis=data['synopsis']
    try:
        anilist_data=fetch_data_anilist(anilist_id)['Media']
    except Exception as e:
        return Response(json.dumps(e.errors[0]), status=500)

    db = SessionLocal()
    x=db.query(AnimeV2).filter_by(mal_id=anilist_data["idMal"]).one_or_none()
    if(x!=None):
        return Response('anime is existed', status=500)
    db.close()
    #save posters
    date=datetime.now().strftime("%A %b %d %H:%M:%S %Y")
    bannerImage=anilist_data['bannerImage']
    coverImage=anilist_data['coverImage']['extraLarge']
    imgContent=requests.get(coverImage).content
    coverImage=coverImage.split("https://s4.anilist.co/file/anilistcdn/")[-1]
    Config.GITHUB_MEDIA.create_file(coverImage, f"Update {date}", imgContent,branch="main")
    if(bannerImage):
        imgContent=requests.get(bannerImage).content
        bannerImage=bannerImage.split("https://s4.anilist.co/file/anilistcdn/")[-1]
        Config.GITHUB_MEDIA.create_file(bannerImage, f"Update {date}", imgContent,branch="main")

    anime=add_to_database(anilist_data,tg_post_id,synopsis)
    new_anime={
        "mal_id": anime.mal_id,
        "title": list(anime.title),
        "year": anime.year,
        "cover_image": anime.cover_image
    }
    new_anime_id = Config.SEARCH_DB.insert_one(new_anime)
    return Response('ok', status=200)






if __name__ == "__main__":
    # app.run(port=7000)
    threading.Thread(target=app.run, args=(
        "0.0.0.0", Config.PORT), daemon=True).start()

    Config.bot.start()
    idle()
    Config.bot.stop()
