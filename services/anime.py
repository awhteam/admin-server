from database.models import AnimeV2
import requests
from config import Config
from gql import gql
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
from sqlalchemy.orm.attributes import flag_modified
import regex
from __main__ import app

async def fetch_data_anilist(anilist_id):
    search_query = gql("""
query ($anime: Int) {
  Media(id: $anime, type: ANIME) {
    id
    title {
      romaji
      english
      native
    }
    idMal
    status
    bannerImage
    seasonYear
    season
    format
    averageScore
    coverImage {
      extraLarge
      color
    }
    episodes
    duration
    
    
  }
}
""")
    async with Config.ANILIST_CLIENT as session:
      fetched_data = await session.execute(
          search_query, variable_values={"anime": anilist_id})
    return fetched_data


def add_to_database(data, postId, synopsis):
    x = app.session.query(AnimeV2).filter_by(mal_id=data["idMal"]).one_or_none()
    if(x != None):
        x.synopsis = synopsis.strip("\n")
        x.tg_main_post = postId
        app.session.commit()
        app.session.close()
        return x
    anime = AnimeV2()
    anime.mal_id = data["idMal"]
    anime.tg_main_post = postId
    anime.title = data["title"]
    anime.status = data["status"]
    anime.banner_image = data["bannerImage"]
    anime.season = data["season"]
    anime.year = data["seasonYear"]
    anime.format = data["format"]
    anime.anilist_score = data["averageScore"]
    anime.cover_image = data["coverImage"]["extraLarge"]
    anime.cover_color = data["coverImage"]["color"]
    anime.episodes = data["episodes"]
    anime.duration = data["duration"]
    # fetch data from mal
    mal_id = data["idMal"]
    mal_data = requests.get(
        f"https://api.jikan.moe/v4/anime/{mal_id}").json()['data']
    anime.mal_score = mal_data['score']
    anime.mal_members = mal_data['scored_by']
    anime.aired_date = mal_data['aired']['from']
    anime.source = mal_data['source']
    anime.genres = [a['mal_id'] for a in mal_data['genres']]
    anime.themes = [a['mal_id'] for a in mal_data['themes']]
    anime.demographics = [a['mal_id'] for a in mal_data['demographics']]
    anime.studios = [a['mal_id'] for a in mal_data['studios']]
    anime.studios_names = {int(s['mal_id']): s['name']
                           for s in mal_data['studios']}
    anime.synopsis = synopsis.strip("\n")
    if(anime.banner_image):
        anime.banner_image = anime.banner_image.replace(
            "https://s4.anilist.co/file/anilistcdn", "")
    anime.cover_image = anime.cover_image.replace(
        "https://s4.anilist.co/file/anilistcdn", "")
    app.session.add(anime)
    app.session.commit()
    app.session.close()
    return anime


async def update_files(mal_id, message: Message):
    # get anime files
    anime = app.session.query(AnimeV2).filter_by(mal_id=mal_id).one_or_none()
    if(not anime):
        return

    post_text = str(message.caption)
    post_urls = "".join([x.url for x in message.caption_entities if x.url])
    # get post files

    fileIds = list(map(int,regex.findall("t.me/AWHTarchive/([0-9]{1,})",post_urls)))   
    files_msg = await Config.bot.get_messages('AWHTarchive', fileIds)
    files = [{"msg_id": f.message_id, "filename": f.document.file_name, "filesize": round(
        f.document.file_size/(1024*1024), 2), } for f in files_msg if f.document]
    print(files)
    is_bluray = ""
    if("#Bluray" in post_text or "#BluRay" in post_text):
        is_bluray = " Bluray"
    files2 = {}
    for r in ["480", "720", "1080"]:
        files2[f"{r}p{is_bluray}"] = {epi.groups(0)[0]: f for f in files if r in f['filename'] and (
            epi := regex.search("\].*[a-zA-Z].*[-Ee ]([0-9]{2,4})[ \[\(.]", f['filename']))}

    # find new one
    new_episodes = {}
    if(anime.files):
        flag_modified(anime, "files")
        for r in ["480", "720", "1080"]:
            quality = f"{r}p{is_bluray}"
            for k, f in files2[quality].items():
                if not k in anime.files[quality].keys() or anime.files[quality][k] != f:
                    print(k)
                    anime.files[quality][k] = f
                    new_episodes[quality] = new_episodes.get(quality, [])+[k]
    else:
        anime.files = files2

    nw_msg = f"**NEW UPDATE**\nAnime: {anime.title.romaji} {anime.year}\n"
    anime.tg_main_post = message.message_id
    anime.tg_post_date = datetime.fromtimestamp(message.date)
    if(message.edit_date):
        anime.tg_post_edit_date = datetime.fromtimestamp(message.edit_date)
    try:
        app.session.commit()
    except:
        app.session.rollback()
    app.session.close()
    print(new_episodes)
    for r, val in new_episodes.items():
        nw_msg += f"کیفیت {r}‏: {','.join(val)}‏\n"

    nw_msg += "\n-------\n"
    await Config.bot.send_message(
        Config.UPDATES_CHANNEL, nw_msg,
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(f"view anime page",
                                      url=f"https://life-edu.ml/anime/{mal_id}")]
            ]))
