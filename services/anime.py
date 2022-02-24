from database.models import AnimeV2
from database.database import SessionLocal
import requests
from config import  Config
from gql import gql

def fetch_data_anilist(anilist_id):
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
    fetched_data = Config.ANILIST_CLIENT.execute(search_query, variable_values={"anime": anilist_id})
    return fetched_data

def add_to_database(data,postId,synopsis):
  db = SessionLocal()
  x=db.query(AnimeV2).filter_by(mal_id=data["idMal"]).one_or_none()
  if(x!=None):
    x.synopsis=synopsis.strip("\n")
    x.tg_main_post = postId
    db.commit()
    db.close()
    return x
  anime= AnimeV2()
  anime.mal_id= data["idMal"]
  anime.tg_main_post = postId
  anime.title = data["title"]
  anime.status = data["status"]
  anime.banner_image = data["bannerImage"]
  anime.season = data["season"]
  anime.year = data["seasonYear"]
  anime.format = data["format"]
  anime.anilist_score= data["averageScore"] 
  anime.cover_image = data["coverImage"]["extraLarge"]
  anime.cover_color = data["coverImage"]["color"]
  anime.episodes= data["episodes"]
  anime.duration= data["duration"]
  #fetch data from mal
  mal_id=data["idMal"]
  mal_data=requests.get(f"https://api.jikan.moe/v4/anime/{mal_id}").json()['data']
  anime.mal_score = mal_data['score']
  anime.mal_members = mal_data['scored_by']
  anime.aired_date = mal_data['aired']['from']
  anime.source = mal_data['source']
  anime.genres = [a['mal_id'] for a in mal_data['genres']]
  anime.themes = [a['mal_id'] for a in mal_data['themes']]
  anime.demographics = [a['mal_id'] for a in mal_data['demographics']]
  anime.studios = [a['mal_id'] for a in mal_data['studios']]
  anime.studios_names={int(s['mal_id']):s['name'] for s in mal_data['studios']}
  anime.synopsis=synopsis.strip("\n")
  if(anime.banner_image):
    anime.banner_image=anime.banner_image.replace("https://s4.anilist.co/file/anilistcdn","")
  anime.cover_image=anime.cover_image.replace("https://s4.anilist.co/file/anilistcdn","")
  db.add(anime)
  db.commit()
  db.close()
  return anime