from pathlib import Path
from discord.ext import commands
import discord.utils
from discord import Emoji
import aiofiles
import logging
from typing import Optional

from .config import EMOJI_PATH
from .utils import get_bot

logger = logging.getLogger(__name__)
AVAILABLE_SUFFIX_EMOJIS = ('.png', '.gif', '.jpg', '.jpeg')

EMOJIS = []

async def create_emojis(bot: commands.Bot):
    global EMOJIS
    await bot.wait_until_ready()
    emojis = await bot.fetch_application_emojis()
    loaded_emoji_counts = 0

    # 優先使用使用者自定義 emoji
    for path in EMOJI_PATH.iterdir():
        if not path.suffix in AVAILABLE_SUFFIX_EMOJIS: continue
        name = path.stem

        if discord.utils.get(emojis, name=name):
            continue

        async with aiofiles.open(path, 'rb') as f:
            image_bytes = await f.read()

        emoji = await bot.create_application_emoji(  
            name=name,  
            image=image_bytes  
        )

        loaded_emoji_counts += 1

    # 如果遇到重複的就會被跳過
    for path in (Path(__file__).parent.parent / 'assets' / 'emojis').iterdir():
        if not path.suffix in AVAILABLE_SUFFIX_EMOJIS: continue
        name = path.stem

        if discord.utils.get(emojis, name=name):
            continue

        async with aiofiles.open(path, 'rb') as f:
            image_bytes = await f.read()

        emoji = await bot.create_application_emoji(  
            name=name,  
            image=image_bytes  
        )

        loaded_emoji_counts += 1

    logger.info(f'Loaded {loaded_emoji_counts} emojis.')
    EMOJIS = await bot.fetch_application_emojis()

async def update_custom_emojis(bot: commands.Bot):
    global EMOJIS
    await bot.wait_until_ready()

    for path in EMOJI_PATH.iterdir():
        if not path.suffix in AVAILABLE_SUFFIX_EMOJIS: continue
        name = path.stem

        emoji = discord.utils.get(EMOJIS, name=name)
        if emoji: # 如果存在的話 就刪除後再更新
            await emoji.delete()

        async with aiofiles.open(path, 'rb') as f:
            image_bytes = await f.read()

        emoji = await bot.create_application_emoji(  
            name=name,  
            image=image_bytes  
        )

    EMOJIS = await bot.fetch_application_emojis()

async def update_default_emojis(bot: commands.Bot):
    global EMOJIS
    await bot.wait_until_ready()

    for path in (Path(__file__).parent.parent / 'assets' / 'emojis').iterdir():
        if not path.suffix in AVAILABLE_SUFFIX_EMOJIS: continue
        name = path.stem

        emoji = discord.utils.get(EMOJIS, name=name)
        if emoji: # 如果存在的話 就刪除後再更新
            await emoji.delete()

        async with aiofiles.open(path, 'rb') as f:
            image_bytes = await f.read()

        emoji = await bot.create_application_emoji(  
            name=name,  
            image=image_bytes  
        )

    EMOJIS = await bot.fetch_application_emojis()

def get_emoji(name: str) -> Optional[Emoji]:
    return discord.utils.get(EMOJIS, name=name) # application emoji can only get from API