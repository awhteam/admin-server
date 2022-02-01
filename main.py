from config import Config
import threading
from flask import Flask, Response, _app_ctx_stack
from flask_cors import CORS
from pyrogram import idle
from database import models
from database.database import SessionLocal, engine, Base
from sqlalchemy.orm import scoped_session

app = Flask(__name__)
models.Base.metadata.create_all(bind=engine)
CORS(app)
app.session = scoped_session(
    SessionLocal, scopefunc=_app_ctx_stack.__ident_func__)
Base.query = app.session.query_property()



@app.route('/', methods=['GET', 'POST'])
def wake():
	return Response('ok', status=200)


if __name__ == "__main__":
    threading.Thread(target=app.run, args=(
        "0.0.0.0", Config.PORT), daemon=True).start()

    Config.bot.start()
    idle()
    Config.bot.stop()
