from config import Config
import threading
from flask import Flask, Response, _app_ctx_stack,request, jsonify, make_response
from flask_cors import CORS
from pyrogram import idle
from database import models
from database.database import SessionLocal, engine, Base
from sqlalchemy.orm import scoped_session
import json
from services.anime import fetch_data_anilist,add_to_database
import requests
import datetime
from database.models import AnimeV2,User
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import jwt
from functools import wraps

app = Flask(__name__)
models.Base.metadata.create_all(bind=engine)
CORS(app)
app.session = scoped_session(
    SessionLocal, scopefunc=_app_ctx_stack.__ident_func__)
Base.query = app.session.query_property()
app.config['SECRET_KEY']='***REMOVED***'


@app.route('/', methods=['GET', 'POST'])
def wake():
	return Response('ok', status=200)


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if 'x-access-tokens' in request.headers:
            token = request.headers['x-access-tokens']

        if not token:
            return jsonify({'message': 'a valid token is missing'})
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user =  app.session.query(models.User).filter_by(username=data['username']).first()
        except:
            return jsonify({'message': 'token is invalid'})

        return f(current_user, *args, **kwargs)
    return decorator


@app.route('/register', methods=['POST'])
def signup_user():  
    data = request.get_json() 
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(username=data['username'], password=hashed_password) 
    app.session.add(new_user)  
    app.session.commit()    
    return jsonify({'message': 'registration successfully'})

@app.route('/login', methods=['POST'])  
def login_user(): 
    auth = request.authorization   

    if not auth or not auth.username or not auth.password:  
        return make_response('could not verify', 401, {'Authentication': 'login required"'})    

    user = app.session.query(User).filter_by(username=auth.username).first()   
     
    if check_password_hash(user.password, auth.password):

        token = jwt.encode({'username' : user.username, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=45)}, app.config['SECRET_KEY'], "HS256")
        return jsonify({'token' : token}) 

    return make_response('could not verify',  401, {'Authentication': '"login required"'})


@app.route('/anime/add', methods=['POST'])
@token_required
def add_new_anime(current_user):
    data= request.get_json() 
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


@app.teardown_appcontext
def remove_session(*args, **kwargs):
    app.session.remove()



if __name__ == "__main__":
    # app.run(port=7000)
    threading.Thread(target=app.run, args=(
        "0.0.0.0", Config.PORT), daemon=True).start()
    Config.vnc_mod_bot.start()
    Config.bot.start()
    idle()
    Config.bot.stop()
    Config.vnc_mod_bot.stop()
