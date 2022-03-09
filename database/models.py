from sqlalchemy import Table, Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import DATE
from sqlalchemy.types import TIMESTAMP,Date
from database.database import Base
from sqlalchemy_utils import CompositeType, JSONType, ScalarListType, ColorType
from sqlalchemy.sql import func
from sqlalchemy_utils import CompositeType
from sqlalchemy_utils.types.pg_composite import CompositeElement

class _CompositeType(CompositeType):
    class comparator_factory(CompositeType.comparator_factory):
        def __getattr__(self, key):
            try:
                type_ = self.type.typemap[key]
            except KeyError:
                raise KeyError(
                    "Type '%s' doesn't have an attribute: '%s'" % (
                        object.__getattribute__(self, 'name'), key
                    )
                )

            return CompositeElement(self.expr, key, type_)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.typemap = dict((col.name, col.type) for col in self.columns)


class Anime(Base):
    __tablename__ = 'animes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    idMal = Column(Integer, unique=True)
    tgPostId = Column(Integer, unique=True, nullable=True)
    modifiedDate = Column(TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp())
    faTitle= Column(String, nullable=True)
    title = Column(
        _CompositeType(
            'title',
            [
                Column('romaji', String),
                Column('english', String),
                Column('native', String)
            ]
        ), nullable=True)
    airedDate = Column(Date, nullable=True)
    season = Column(String, nullable=True)
    season2 = Column(String, nullable=True)
    format = Column(String, nullable=True)
    status = Column(String, nullable=True)
    source = Column(String, nullable=True)
    genres = Column(ScalarListType(int), nullable=True)
    themes = Column(ScalarListType(int), nullable=True)
    demographics = Column(ScalarListType(int), nullable=True)
    studios = Column(ScalarListType(int), nullable=True)
    seasonYear = Column(Integer, nullable=True)
    episodesNo = Column(Integer, nullable=True)
    duration = Column(String, nullable=True)
    malScore = Column(Float, nullable=True)
    malMembers = Column(Float, nullable=True)
    anilistScore = Column(Float, nullable=True)
    coverImage = Column(String, nullable=True)
    coverColor = Column(ColorType, nullable=True)
    bannerImage = Column(String, nullable=True)
    licensedBy = Column(String, nullable=True)
    Synopsis = Column(String, nullable=True)
    Files = Column(JSONType, nullable=True)
    trailer=Column(String, nullable=True)

    def __repr__(self):
        return "<Anime(title='%s', idMal='%d')>" % (self.title.english, self.idMal)



class AnimeV2(Base):
    __tablename__ = 'animes_v2'

    id = Column(Integer, primary_key=True, autoincrement=True)
    mal_id = Column(Integer, unique=True)
    title = Column(
        _CompositeType(
            'title',
            [
                Column('romaji', String),
                Column('english', String),
                Column('native', String)
            ]
        ), nullable=True)
    farsi_titles= Column(ScalarListType(str), nullable=True)
    season = Column(String, nullable=True)
    year = Column(Integer, nullable=True)
    episodes = Column(Integer, nullable=True)
    duration = Column(String, nullable=True)
    tg_main_post = Column(Integer, unique=True, nullable=True)
    synopsis = Column(String, nullable=True)
    format = Column(String, nullable=True)
    status = Column(String, nullable=True)
    source = Column(String, nullable=True)
    mal_score = Column(Float, nullable=True)
    mal_members = Column(Float, nullable=True)
    anilist_score = Column(Float, nullable=True)
    tg_posts = Column(ScalarListType(int), nullable=True)
    tg_post_date = Column(TIMESTAMP,nullable=True)
    tg_post_edit_date = Column(TIMESTAMP,nullable=True)
    modified_date = Column(TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp())
    aired_date = Column(Date, nullable=True)
    genres = Column(ScalarListType(int), nullable=True)
    themes = Column(ScalarListType(int), nullable=True)
    demographics = Column(ScalarListType(int), nullable=True)
    studios = Column(ScalarListType(int), nullable=True)
    studios_names = Column(JSONType, nullable=True)
    cover_image = Column(String, nullable=True)
    cover_color = Column(String, nullable=True)
    banner_image = Column(String, nullable=True)
    trailer=Column(String, nullable=True)
    files = Column(JSONType, nullable=True)
    collection = Column(Integer, ForeignKey('anime_collections.id'), nullable=True)
    def __repr__(self):
        return "<AnimeV2(title='%s', mal_id='%d',tg_main_post='%d')>" % (self.title.english, self.mal_id,self.tg_main_post)


class AnimeCollection(Base):
    __tablename__ = 'anime_collections'
    id = Column(Integer, primary_key=True, autoincrement=True)
    tg_main_post = Column(Integer, unique=True)
    animes = relationship("AnimeV2")


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String,unique=True)
    password = Column(String)