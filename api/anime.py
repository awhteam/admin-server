

from config import Config
from flask import Response,request, jsonify, make_response
import json
from services.anime import fetch_data_anilist,add_to_database,update_files
import requests
import datetime
from database.models import AnimeV2,User
import jwt
from functools import wraps
from __main__ import app

def token_required(f):
    @wraps(f)
    async def decorator(*args, **kwargs):
        token = None
        if 'x-access-tokens' in request.headers:
            token = request.headers['x-access-tokens']

        if not token:
            return make_response('could not verify', 401, {'message': 'a valid token is missing'})    
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user =  app.session.query(User).filter_by(username=data['username']).first()
        except:
            return make_response('could not verify', 401, {'message': 'token is invalid'})    

        return await f(current_user, *args, **kwargs)
    return decorator


@app.route('/anime/add', methods=['POST'])
@token_required
async def add_new_anime(current_user):
    data= request.get_json() 
    anilist_id=data['anilist_id']
    tg_post_id=data['tg_post_id']
    synopsis=data['synopsis']
    try:
        anilist_data=(await fetch_data_anilist(anilist_id))['Media']
    except Exception as e:
        return Response(json.dumps(e.errors[0]), status=500)

    x= app.session.query(AnimeV2).filter_by(mal_id=anilist_data["idMal"]).one_or_none()
    if(x!=None):
        return Response('anime is existed', status=500)
    app.session.close()
    #save posters
    date=datetime.datetime.now().strftime("%A %b %d %H:%M:%S %Y")
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
        "title": anime.title,
        "year": anime.year,
        "cover_image": anime.cover_image
    }
    new_anime_id = Config.SEARCH_DB.insert_one(new_anime)
    return Response('ok', status=200)



@app.route('/anime/files', methods=['POST'])
@token_required
async def update_anime_files_api(current_user):
    data= request.get_json() 
    mal_id=data['mal_id']
    tg_post_ids=[int(x) for x in data['tg_post_ids'].split(",")]
    post_messages = await Config.bot.get_messages("animworlddl",tg_post_ids)
    for post_msg in post_messages:
        await update_files(mal_id,post_msg)
    return Response('ok', status=200)
