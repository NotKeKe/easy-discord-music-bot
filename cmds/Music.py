import discord
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands, tasks
import logging
import copy
from typing import Optional
from datetime import datetime

from cmds.music_bot import utils
from cmds.music_bot.autocomplete import *
from cmds.music_bot.buttons import *
from cmds.music_bot.player import Player, loop_option
from cmds.music_bot.play_list import CustomListPlayer, add_to_custom_list, get_custom_list, del_custom_list
from cmds.music_bot.utils import send_info_embed, check_and_get_player, players, join_channel_time, custom_list_players

from core.translator import locale_str, get_translate, load_translated
from core.utils import create_basic_embed
from core.config import resource_path

logger = logging.getLogger(__name__)

# load opus
if not discord.opus.is_loaded():
    import platform
    if platform.architecture()[0] == '64bit':
        discord.opus.load_opus(resource_path('assets/opus/opus_x64.dll'))
    elif platform.architecture()[0] == '32bit':
        discord.opus.load_opus(resource_path('assets/opus/opus_x86.dll'))

# if still not load opus
if not discord.opus.is_loaded():
    raise Exception('Failed to load opus')

class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self):
        logger.info(f'Loaded "{__name__}"')

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        '''用於檢測 bot 加入語音頻道，並紀錄時間'''
        guild_id = member.guild.id
        if not self.bot.user: return
        if member.id == self.bot.user.id:
            if before.channel is None and after.channel is not None: # 加入語音頻道
                join_channel_time[guild_id] = datetime.now()
            elif before.channel is not None and after.channel is None: # 離開語音頻道
                if guild_id in join_channel_time:
                    del join_channel_time[guild_id]
            elif before.channel is not None and after.channel is not None: # 切換語音頻道
                join_channel_time[guild_id] = datetime.now()
        else: # 普通使用者 or 其他 bot
            if member.bot: return
            just_self_deafened = not before.self_deaf and after.self_deaf
            just_deafened_by_server = not before.deaf and after.deaf

            if not (just_self_deafened or just_deafened_by_server): # 如果不是 (使用者開啟拒聽 or 使用者被伺服器拒聽)
                return
            
            if guild_id in join_channel_time: # 如果確定 bot 在語音頻道，再更新
                join_channel_time[guild_id] = datetime.now()

    @commands.hybrid_command(name=locale_str('play'), description=locale_str('play'), aliases=['p', '播放'])
    @app_commands.describe(query=locale_str('play_query'))
    @app_commands.autocomplete(query=play_query_autocomplete)
    async def _play(self, ctx: commands.Context, *, query: Optional[str] = None):
        if not ctx.guild: return
        try:
            async with ctx.typing():
                member = ctx.guild.get_member(ctx.author.id) or await ctx.guild.fetch_member(ctx.author.id) if ctx.guild else None
                if not member:
                    return await ctx.send(await get_translate('send_play_not_in_guild', ctx))

                if not member.voice: return await ctx.send(await get_translate('send_play_not_in_voice', ctx))
                if not ctx.voice_client and member.voice.channel:
                    await member.voice.channel.connect()

                if ctx.voice_client.is_paused(): return await ctx.invoke(self.bot.get_command('resume')) # type: ignore
                elif not query: return await ctx.send(await get_translate('send_play_no_query', ctx))
                if players.get(ctx.guild.id): return await ctx.invoke(self.bot.get_command('add'), query=query) # type: ignore

                player = Player(ctx)
                players[ctx.guild.id] = player
                data = await player.add(query, ctx)
                await player.play()
                await send_info_embed(player, ctx)
        except:
            logger.error('Error while /play', exc_info=True)
            await ctx.send(await get_translate('send_play_error', ctx))
            if ctx.guild.id in players:
                del players[ctx.guild.id]

    @commands.hybrid_command(name=locale_str('add'), description=locale_str('add'))
    @app_commands.describe(query=locale_str('add_query'))
    @app_commands.autocomplete(query=play_query_autocomplete)
    async def _add(self, ctx: commands.Context, *, query: str):
        if not ctx.guild: return
        async with ctx.typing():
            member = ctx.guild.get_member(ctx.author.id) or await ctx.guild.fetch_member(ctx.author.id) if ctx.guild else None
            if not member:
                return await ctx.send(await get_translate('send_play_not_in_guild', ctx))

            if not member.voice: return await ctx.send(await get_translate('send_add_not_in_voice', ctx))
            if not ctx.voice_client: return await ctx.send(await get_translate('send_add_use_play_first', ctx))
            if member.voice.channel != ctx.voice_client.channel: return await ctx.send((await get_translate('send_add_not_in_same_channel')).format(channel_mention=ctx.guild.voice_client.channel.mention)) # type: ignore , prob has some problems here, but idk

            try:
                player: Optional[Player] = players.get(ctx.guild.id)
                if not player: return await ctx.send(await get_translate('send_add_player_crashed', ctx))

                data = await player.add(query, ctx)
                size = data[0] if data else 1

                await send_info_embed(player, ctx, size-1)
                await ctx.send((await get_translate('send_add_success', ctx)).format(size=size), ephemeral=True)
            except:
                logger.error('Error while /add', exc_info=True)

    @commands.hybrid_command(name=locale_str('skip'), description=locale_str('skip'), aliases=['s'])
    async def _skip(self, ctx: commands.Context):
        async with ctx.typing():
            player, status = await check_and_get_player(ctx)
            if not status: return
            assert isinstance(player, Player)

            if not (await player.skip()): return await ctx.send(await get_translate('send_skip_no_more_songs', ctx))

            await send_info_embed(player, ctx)

    @commands.hybrid_command(name=locale_str('back'), description=locale_str('back'))
    async def _back(self, ctx: commands.Context):
        async with ctx.typing():
            player, status = await check_and_get_player(ctx)
            if not status: return
            assert isinstance(player, Player)
            
            if not (await player.back()): return await ctx.send(await get_translate('send_back_no_more_songs', ctx))

            await send_info_embed(player, ctx)

    @commands.hybrid_command(name=locale_str('pause'), description=locale_str('pause'), aliases=['ps', '暫停'])
    async def _pause(self, ctx: commands.Context):
        async with ctx.typing():
            player, status = await check_and_get_player(ctx)
            if not status: return
            assert isinstance(player, Player)

            await player.pause(ctx)
    
    @commands.hybrid_command(name=locale_str('resume'), description=locale_str('resume'), aliases=['rs'])
    async def resume(self, ctx: commands.Context):
        async with ctx.typing():
            player, status = await check_and_get_player(ctx)
            if not status: return
            assert isinstance(player, Player)

            # 修正邏輯：當暫停時才恢復播放
            await player.resume(ctx)

    @commands.hybrid_command(name=locale_str('stop'), description=locale_str('stop'))
    async def _stop(self, ctx: commands.Context):
        if not ctx.guild: return
        async with ctx.typing():
            member = ctx.guild.get_member(ctx.author.id) or await ctx.guild.fetch_member(ctx.author.id) if ctx.guild else None
            if not member:
                return await ctx.send(await get_translate('send_play_not_in_guild', ctx))
            
            if not (member.voice and ctx.voice_client): return await ctx.send(await get_translate('send_stop_not_in_voice', ctx))
            if member.voice.channel != ctx.voice_client.channel: return await ctx.send(await get_translate('send_stop_not_in_same_channel', ctx))
            channel = ctx.voice_client.channel
            await utils.leave(ctx)
            await ctx.send((await get_translate('send_stop_success', ctx)).format(channel_mention=channel.mention)) # type: ignore

    @commands.hybrid_command(name=locale_str('loop'), description=locale_str('loop'))
    @app_commands.choices(loop_type = [Choice(name=item, value=item) for item in loop_option])
    @app_commands.describe(loop_type=locale_str('loop_loop_type'))
    async def _loop(self, ctx: commands.Context, loop_type: Optional[str] = None):
        async with ctx.typing():
            loop_option_str = ', '.join(loop_option)
            if loop_type not in loop_option and loop_type is not None: return await ctx.send((await get_translate('send_loop_invalid_type', ctx)).format(loop_option_str=loop_option_str))

            player, status = await check_and_get_player(ctx)
            if not status: return
            assert isinstance(player, Player)

            if loop_type is not None:
                player.loop(loop_type)
            else:
                loop_type = player.turn_loop()

            await ctx.send((await get_translate('send_loop_success', ctx)).format(loop_type=loop_type))

    @commands.hybrid_command(name=locale_str('nowplaying'), description=locale_str('nowplaying'), aliases=['np', '當前播放', 'now'])
    async def current_playing(self, ctx: commands.Context):
        async with ctx.typing():
            player, status = await check_and_get_player(ctx, check_user_in_channel=False)
            if not status: return
            assert isinstance(player, Player)

            await send_info_embed(player, ctx)

    @commands.hybrid_command(name=locale_str('queue'), description=locale_str('queue'), aliases=['q', '清單'])
    async def _list(self, ctx: commands.Context):
        async with ctx.typing():
            player, status = await check_and_get_player(ctx, check_user_in_channel=False)
            if not status: return
            assert isinstance(player, Player)

            eb = await player.show_list()

            await ctx.send(embed=eb)

    @commands.hybrid_command(name=locale_str('remove'), description=locale_str('remove'), aliases=['rm', '刪除'])
    @app_commands.describe(number=locale_str('remove_number'))
    async def delete_song(self, ctx: commands.Context, number: int):
        async with ctx.typing():
            player, status = await check_and_get_player(ctx)
            if not status: return
            assert isinstance(player, Player)

            item = player.delete_song(number - 1)

            await ctx.send((await get_translate('send_remove_success', ctx)).format(title=item.get('title'), user_name=item.get('user').global_name))

    @commands.hybrid_command(name=locale_str('clear'), description=locale_str('clear'), aliases=['cq', '清除'])
    async def clear_queue(self, ctx: commands.Context):
        try:
            async with ctx.typing():
                player, status = await check_and_get_player(ctx)
                if not status: return
                assert isinstance(player, Player)
                if not player.list: return await ctx.send(await get_translate('send_clear_already_empty', ctx))

                view = discord.ui.View(timeout=60)
                button_check = discord.ui.Button(emoji='✅', label=await get_translate('send_clear_confirm_button', ctx), style=discord.ButtonStyle.green)
                async def clear_queue_callback(interaction: discord.Interaction):
                    player.clear_list()
                    button_reject.disabled = True
                    button_check.disabled = True
                    await interaction.response.edit_message(content=await interaction.translate('send_clear_success'), embed=None, view=None)
                button_check.callback = clear_queue_callback

                button_reject = discord.ui.Button(emoji='❌', label=await get_translate('send_clear_reject_button', ctx), style=discord.ButtonStyle.red)
                async def button_reject_callback(interaction: discord.Interaction):
                    button_reject.disabled = True
                    button_check.disabled = True
                    await interaction.response.edit_message(content=await interaction.translate('send_clear_cancelled'), embed=None, view=None)
                button_reject.callback = button_reject_callback

                view.add_item(button_check)
                view.add_item(button_reject)

                '''i18n'''
                eb = load_translated((await get_translate('embed_clear_confirm', ctx)))[0]
                title = eb.get('title')
                ''''''

                eb = create_basic_embed(title, color=ctx.author.color)
                eb.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
                await ctx.send(embed=eb, view=view)
        except:
            logger.error('Error while /clear.', exc_info=True)

    @commands.hybrid_command(name=locale_str('leave'), description=locale_str('leave'))
    async def _leave(self, ctx: commands.Context):
        await ctx.invoke(self.bot.get_command('stop')) # type: ignore

    # @commands.hybrid_command(name=locale_str('lyrics'), description=locale_str('lyrics'))
    # @app_commands.describe(query=locale_str('lyrics_query'), artist=locale_str('lyrics_artist'), lrc=locale_str('lyrics_lrc'))
    # async def lyrics_search(self, ctx: commands.Context, query: str, artist: Optional[str] = None, lrc: bool = False):
    #     async with ctx.typing():
    #         result = await search_lyrics(query, artist, lrc)
    #         await ctx.send(result if result else await get_translate('send_lyrics_not_found'))

    #         if not isinstance(result, str): return

    #         if len(result.splitlines()) < 10: await ctx.send(await get_translate('send_lyrics_too_short_tip'), ephemeral=True)

    @commands.hybrid_command(name=locale_str('volume'), description=locale_str('volume'))
    @app_commands.describe(volume=locale_str('volume_volume'))
    async def volume_adjust(self, ctx: commands.Context, volume: Optional[int] = None):
        async with ctx.typing():
            player, status = await check_and_get_player(ctx)
            if not status: return
            assert isinstance(player, Player)

            if volume:
                await player.volume_adjust(volume=volume / 100)

            await ctx.send(await get_translate('send_volume_buttons_title', ctx), view=VolumeControlButtons(player))

    @commands.hybrid_command(name=locale_str('play_custom_list'), description=locale_str('play_custom_list'))
    @app_commands.autocomplete(list_name=custom_play_list_autocomplete)
    async def play_custom_list(self, ctx: commands.Context, list_name: str):
        if not ctx.guild: return
        async with ctx.typing():
            member = ctx.guild.get_member(ctx.author.id) or await ctx.guild.fetch_member(ctx.author.id) if ctx.guild else None
            if not member:
                return await ctx.send(await get_translate('send_play_not_in_guild', ctx))

            if not member.voice: return await ctx.send(await get_translate('send_play_not_in_voice', ctx))
            if players.get(ctx.guild.id): # 不讓使用者同時播放兩個 list，或是自訂歌曲 + 自訂歌單
                return await ctx.send(await get_translate('send_play_custom_list_already_playing_left_first', ctx))
            if not ctx.voice_client and member.voice.channel:
                await member.voice.channel.connect()

            if ctx.voice_client.is_paused(): return await ctx.invoke(self.bot.get_command('resume')) # type: ignore
            if players.get(ctx.guild.id): return # 如果 player 已經存在，則不再建立
            
            # 取得 player
            custom_list_player = CustomListPlayer(ctx, list_name)
            player = await custom_list_player.run()
            players[ctx.guild.id] = player
            custom_list_players[ctx.guild.id] = custom_list_player

            # 播放
            await player.play()
            await send_info_embed(player, ctx)
            
    @commands.hybrid_command(name=locale_str('add_custom_list'), description=locale_str('add_custom_list'))
    @app_commands.autocomplete(list_name=custom_play_list_autocomplete)
    @app_commands.describe(list_name=locale_str('add_custom_list_list_name'))
    async def add_custom_list(self, ctx: commands.Context, url: str, list_name: str):
        async with ctx.typing():
            result = await add_to_custom_list(url, list_name, ctx.author.id)
            await ctx.send(result if result is not True else (await get_translate('send_add_to_custom_list_success', ctx)).format(list_name=list_name)) # type: ignore

    @commands.hybrid_command(name=locale_str('show_custom_list'), description=locale_str('show_custom_list'))
    @app_commands.autocomplete(list_name=custom_play_list_autocomplete)
    async def show_custom_list(self, ctx: commands.Context, list_name: str):
        async with ctx.typing():
            result = await get_custom_list(list_name, ctx.author.id)
            description = '\n'.join(f'{i+1}. [{song[0]}]({song[1]})' for i, song in enumerate(result))
            eb = create_basic_embed(description=description)
            await ctx.send(embed=eb)

    @commands.hybrid_command(name=locale_str('delete_custom_list'), description=locale_str('delete_custom_list'), aliases=['del_custom_list'])
    @app_commands.autocomplete(list_name=custom_play_list_autocomplete)
    async def delete_custom_list(self, ctx: commands.Context, list_name: str):
        async with ctx.typing():
            view = discord.ui.View(timeout=60)
            button_check = discord.ui.Button(emoji='✅', label='Yes', style=discord.ButtonStyle.green)
            async def button_check_callback(interaction: discord.Interaction):
                button_reject.disabled = True
                button_check.disabled = True

                await del_custom_list(list_name, interaction.user.id)

                await interaction.response.edit_message(content=await interaction.translate('send_delete_custom_list_success'), embed=None, view=None)
            button_check.callback = button_check_callback

            button_reject = discord.ui.Button(emoji='❌', label='No', style=discord.ButtonStyle.red)
            async def button_reject_callback(interaction: discord.Interaction):
                button_reject.disabled = True
                button_check.disabled = True
                await interaction.response.edit_message(content=await interaction.translate('send_delete_custom_list_cancelled'), embed=None, view=None)
            button_reject.callback = button_reject_callback

            view.add_item(button_check)
            view.add_item(button_reject)

            '''i18n'''
            eb = load_translated((await get_translate('embed_clear_confirm', ctx)))[0]
            title = eb.get('title')
            ''''''

            eb = create_basic_embed(title, color=ctx.author.color)
            eb.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
            await ctx.send(embed=eb, view=view)

    @tasks.loop(minutes=1)
    async def check_left_channel(self):
        for guild_id, time in copy.deepcopy(join_channel_time).items(): # 使用 deepcopy，避免迴圈途中被進行修改
            guild = self.bot.get_guild(guild_id) or await self.bot.fetch_guild(guild_id)
            if not guild:
                try: del join_channel_time[guild_id]
                except: ... # 可能在操作途中 使用者就把 bot 退掉了
                continue
            
            voice_client = guild.voice_client
            if not voice_client:
                try: del join_channel_time[guild_id]
                except: ... # 可能在操作途中 使用者就把 bot 退掉了
                continue
            channel = voice_client.channel

            curr_time = datetime.now()
            passed_time = (curr_time - time).total_seconds()

            if passed_time <= 120: continue # 只檢測超過 2 分鐘的 voice_client

            # 檢測 channel 裡面有沒有活人
            is_alive = False
            for member in channel.members: # type: ignore
                assert isinstance(member, discord.Member)
                if member.id == self.bot.user.id: continue # type: ignore
                voice_state = member.voice
                if not voice_state: continue
                
                afk = voice_state.afk
                deaf = voice_state.deaf
                self_deaf = voice_state.self_deaf

                if not (afk or deaf or self_deaf):
                    is_alive = True
                    break

            if is_alive: 
                if guild_id in join_channel_time:
                    join_channel_time[guild_id] = datetime.now() # 2 分鐘後再判斷，避免短時間內重複判斷
                continue

            successful_run = True # 因為可能遇到途中就已經被刪掉，True 代表過程中完全沒被刪掉
            # 先清除其他變數中的 guild_id，因為 disconnect 會觸發刪除 join_channel_id
            try: del players[guild_id]
            except: successful_run = False
            try: del custom_list_players[guild_id]
            except: ...
            try: del join_channel_time[guild_id]
            except: successful_run = False
            try: await voice_client.disconnect() # type: ignore
            except: successful_run = False


            # 想想還是算了，因為 voice channel 那裡有個白點看著挺煩的:)
            # if successful_run: 
            #     sent_message = await self.bot.tree.translator.get_translate('send_check_left_channel_disconnect_success', guild.preferred_locale.value)
            #     await channel.send(sent_message, silent=True)

    @check_left_channel.before_loop
    async def check_left_channel_before_loop(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Music(bot))