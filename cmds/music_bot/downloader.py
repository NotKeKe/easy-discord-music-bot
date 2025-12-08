import yt_dlp
from pytubefix import AsyncYouTube
from datetime import datetime
import asyncio
from concurrent.futures import ProcessPoolExecutor
import logging
import uuid
import httpx

from . import utils
from .utils import get_video_id, check_audio_url_alive, QUEUE

from core.utils import redis_client, secondToReadable, math_round
from core.mongodb import MongoDB_DB, update_one, find_one

logger = logging.getLogger(__name__)

def extract_info_yt_dlp(video_url: str):
    with yt_dlp.YoutubeDL(utils.YTDL_OPTIONS) as ydl: # type: ignore
        info = ydl.extract_info(video_url, download=False)
        return {
            "audio_url": info.get("url"),
            "thumbnail_url": info.get("thumbnail"),
            "title": info.get("title"),
            "duration": info.get("duration"),
        }
    
async def extract_info_pytube(video_url: str):
    video_id = get_video_id(video_url)
    thumbnail_url = f'https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg'

    yt = AsyncYouTube(video_url)
    streams = await yt.streams()
    best_audio = streams.filter(only_audio=True).order_by('abr').desc().first()

    # get best thumbnail url
    try:
        async with httpx.AsyncClient() as client:
            response = await client.head(thumbnail_url)
            response.raise_for_status()
    except:
        thumbnail_url = await yt.thumbnail_url()

    return {
        "audio_url": best_audio.url if best_audio is not None else '',
        "thumbnail_url": thumbnail_url,
        "title": await yt.title(),
        "duration": await yt.length(),
    }

async def extract_info(video_url: str) -> dict:
    loop = asyncio.get_running_loop()
    with ProcessPoolExecutor() as executor:
        result = await loop.run_in_executor(executor, extract_info_yt_dlp, video_url)

    # check if audio url from yt-dlp is available, else use pytubefix
    if not (await check_audio_url_alive(result["audio_url"])): 
        result = await extract_info_pytube(video_url)

    return result

class RedisTemp:
    redis_base_key = 'musics:'

    @classmethod
    async def search(cls, video_url: str) -> dict | None:
        video_id = get_video_id(video_url)
        if not video_id: return

        key = cls.redis_base_key + video_id

        # find from redis first. Probably useless, idk why
        data = await redis_client.hgetall(key) # type: ignore
        if data:
            d = data.copy()

            audio_url = d['audio_url']
            # 確認 audio url 可用，不用特別刪除，因為後面在搜尋一次時，就會覆蓋掉原本的 key
            if (await check_audio_url_alive(audio_url)):
                logger.info(f"Song {video_url} found from redis.")
                return d | {'duration_int': int(d['duration_int'])}
            
        # find from mongodb
        doc = await find_one(MongoDB_DB.music['temp_urls'], {'video_id': video_id})
        if doc and await check_audio_url_alive(doc.get('audio_url', '')):
            logger.info(f"Song {video_url} found from MongoDB.")
            return doc

    @classmethod
    async def upload(cls, title, video_url, audio_url, thumbnail_url, duration, duration_int):
        video_id = get_video_id(video_url)
        if not video_id: return

        # upload to redis
        key = cls.redis_base_key + video_id

        data = {
            'title': title,
            'video_url': video_url,
            'audio_url': audio_url,
            'thumbnail_url': thumbnail_url,
            'duration': duration,
            'duration_int': duration_int
        }

        await redis_client.hset(key, mapping=data) # type: ignore
        await redis_client.expire(key, 60*60) # 60 分鐘後過期

        # upload to mongodb
        await update_one(
            MongoDB_DB.music['temp_urls'], 
            {'video_id': video_id}, 
            {"$set": data},
            upsert=True
        )

class Downloader:
    '''User await Downloader(query).run()'''
    def __init__(self, query: str, priority: int = 1):
        self.query = query
        self.priority = priority

        self.title = None
        self.video_url = None
        self.audio_url = None
        self.thumbnail_url = None
        self.duration = None
        self.duration_int = None

        self.start_time = datetime.now()
        self.process_time = 0
        self.task_id = str(uuid.uuid4())

    def get_info(self) -> tuple:
        '''return (title, video_url, audio_url, thumbnail_url, duration)'''
        return (self.title, self.video_url, self.audio_url, self.thumbnail_url, self.duration, self.duration_int)

    async def get_url(self):
        if utils.is_url(self.query):
            self.video_url = self.query
        else:
            # self.title, self.video_url, self.duration = utils.query_search(self.query)
            r = await asyncio.to_thread(utils.query_search, self.query)
            if r:
                self.title, self.video_url, self.duration = r

    async def to_audio(self):
        if not self.video_url: print('Please get_url first'); return

        cache = await RedisTemp.search(self.video_url)
        if cache:
            for key, value in cache.items():
                setattr(self, key, value)
            return

        # 基本上 如果是來自播放清單 後面的歌曲，優先級應該要比較低
        await QUEUE.add_task(self.task_id, self.priority, extract_info(self.video_url))
        result = await QUEUE.get_result(self.task_id)

        # 更新 self 的屬性
        self.audio_url = result["audio_url"]
        self.thumbnail_url = result["thumbnail_url"]
        self.title = result["title"]
        self.duration = secondToReadable(result["duration"])
        self.duration_int = result["duration"]

        self.process_time = math_round((datetime.now() - self.start_time).total_seconds(), 0)

        # add to redis
        func = RedisTemp.upload(self.title, self.video_url, self.audio_url, self.thumbnail_url, self.duration, self.duration_int)
        asyncio.create_task(func)

    async def run(self):
        await self.get_url()
        await self.to_audio()