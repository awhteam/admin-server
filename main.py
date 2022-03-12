from config import Config
import threading
from flask import Flask, Response, _app_ctx_stack,request, jsonify, make_response
from flask_cors import CORS
from pyrogram import idle
from database import models
from database.database import SessionLocal, engine, Base
from sqlalchemy.orm import scoped_session
import datetime
from database.models import User
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from functools import wraps
app = Flask(__name__)
models.Base.metadata.create_all(bind=engine)
CORS(app)
app.session = scoped_session(
    SessionLocal, scopefunc=_app_ctx_stack.__ident_func__)
Base.query = app.session.query_property()
app.config['SECRET_KEY']='***REMOVED***'

# import apis
import api.anime

@app.route('/', methods=['GET', 'POST'])
def wake():
	return Response('ok', status=200)



@app.route('/register', methods=['POST'])
async def signup_user():  
    data = request.get_json() 
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(username=data['username'], password=hashed_password) 
    app.session.add(new_user)  
    app.session.commit()    
    return jsonify({'message': 'registration successfully'})

@app.route('/login', methods=['POST'])  
async def login_user(): 
    auth = request.authorization   

    if not auth or not auth.username or not auth.password:  
        return make_response('could not verify', 401, {'Authentication': 'login required"'})    

    user = app.session.query(User).filter_by(username=auth.username).first()   
     
    if check_password_hash(user.password, auth.password):

        token = jwt.encode({'username' : user.username, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(days=1)}, app.config['SECRET_KEY'], "HS256")
        return jsonify({'token' : token}) 

    return make_response('could not verify',  401, {'Authentication': '"login required"'})


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
