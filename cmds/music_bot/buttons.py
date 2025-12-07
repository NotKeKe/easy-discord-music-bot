from discord import Interaction, SelectOption, Message, errors, File
from discord.ui import View, button, select, Button
from discord.ext import commands
import traceback
import asyncio
from typing import Optional

from .player import Player
from .utils import send_info_embed
from .utils import players

from core.utils import get_bot, get_member
from core.translator import get_translate
from core.emojis import get_emoji

# deepwiki help to get emoji
class MusicControlButtons(View):  
    def __init__(self, player: Player, ctx: commands.Context | Interaction, timeout=180):  
        super().__init__(timeout=timeout)  
        self.player = player  
        self.bot = get_bot()  
        self.ctx = ctx
        self.locale = self.lang_code = self._get_lang_code() or player.locale
          
        # 初始化按鈕  
        self._setup_btns()

    def _get_lang_code(self):
        lang_code = None
        if isinstance(self.ctx, commands.Context) and self.ctx.interaction:
            lang_code = self.ctx.interaction.locale.value
        elif isinstance(self.ctx, Interaction):
            lang_code = self.ctx.locale.value
        
        # get guild locale
        if lang_code is None and self.ctx.guild:
            lang_code = self.ctx.guild.preferred_locale.value

        return lang_code

    def _setup_btns(self):
        btn_configs = [ # default config
            ('previous', '⏮️', 'button_previous', self.previous_callback),  
            ('pause', '⏸️', 'button_pause', self.pause_resume_callback),  
            ('next', '⏭️', 'button_next', self.next_callback),  
            ('stop', '⏹️', 'button_stop', self.stop_callback),  
            ('loop', '🔁', 'button_loop', self.loop_callback),  
            ('list', '📋', 'button_list', self.queue_callback),  
            ('refresh', '🔄', 'button_refresh', self.refresh_callback),  
            ('volume', '🔊', 'button_volume', self.volume_callback),  
        ]

        for name, emoji, label_code, callback in btn_configs:
            # get emoji
            _emoji = get_emoji(name)
            if _emoji:
                emoji = _emoji

            # get translation
            _label = self.bot.tree.translator.get_translate_sync(label_code, self.lang_code) # type: ignore
            if _label != label_code:
                label = _label
            else:
                label = label_code

            # create button
            button = Button(
                label=label,
                emoji=emoji,
            )
            button.callback = callback
            self.add_item(button)

      
    async def button_error(self, inter: Interaction, exception):  
        traceback.print_exc()
        if isinstance(exception, errors.Forbidden):  
            try:
                bot = get_bot()  
                u = bot.get_user(inter.user.id) or await bot.fetch_user(inter.user.id)  
                await u.send("I'm missing some permissions:((")  
            except: ...
      
    # 移除所有 @button 裝飾器，改為普通方法  
    async def previous_callback(self, interaction: Interaction):  
        try:  
            await self.player.back()  
            await send_info_embed(self.player, interaction)  
        except Exception as e:  
            await self.button_error(interaction, e)  
  
    async def pause_resume_callback(self, interaction: Interaction):  
        try:  
            if self.player.paused:  
                await self.player.resume()  
            else:  
                await self.player.pause()  
            r = await send_info_embed(self.player, interaction, if_send=False)  
            if r is None: return  
            embed, view = r  
            await interaction.response.edit_message(embed=embed, view=view)  
        except Exception as e:  
            await self.button_error(interaction, e)  
  
    async def next_callback(self, interaction: Interaction):  
        try:  
            await self.player.skip()  
            await send_info_embed(self.player, interaction)  
        except Exception as e:  
            await self.button_error(interaction, e)  
  
    async def stop_callback(self, interaction: Interaction):  
        try:  
            if not interaction.guild: return  
            member = await get_member(interaction)  
            if not member: return  
              
            if not member.voice:   
                return await interaction.response.send_message(  
                    await get_translate('send_button_not_in_voice', interaction, self.locale)  
                )  
            if not interaction.guild.voice_client:   
                return await interaction.response.send_message(  
                    await get_translate('send_button_bot_not_in_voice', interaction, self.locale)  
                )  
  
            player: Optional[Player] = players.get(interaction.guild.id)  
            user = interaction.user.global_name  
  
            if not player:   
                return await interaction.response.send_message(  
                    await get_translate('send_button_player_crashed', interaction, self.locale)  
                )  
            del players[interaction.guild.id]  
  
            await interaction.guild.voice_client.disconnect() # type: ignore
            await interaction.response.send_message(  
                (await get_translate('send_button_stopped_music', interaction, self.locale)).format(  
                    user=user,   
                    channel_mention=player.ctx.channel.mention # type: ignore
                ),   
                ephemeral=True  
            )  
        except Exception as e:  
            await self.button_error(interaction, e)  
  
    async def loop_callback(self, interaction: Interaction):  
        try:  
            msg = interaction.message  
            self.player.turn_loop()  
            r = await send_info_embed(self.player, interaction, if_send=False)  
            if r is None: return  
            eb, view = r  
            if msg:  
                await msg.edit(embed=eb, view=view)  
                  
            new_msg = await interaction.response.send_message(  
                (await get_translate('send_button_loop_changed', interaction, self.locale)).format(  
                    loop_status=self.player.loop_status  
                ),   
                ephemeral=True  
            )  
            if new_msg.resource:  
                await new_msg.resource.delete(delay=30) # type: ignore
        except Exception as e:  
            await self.button_error(interaction, e)  
      
    async def queue_callback(self, interaction: Interaction):  
        try:  
            eb = await self.player.show_list()  
            await interaction.response.send_message(embed=eb, ephemeral=True)  
        except Exception as e:  
            await self.button_error(interaction, e)  
  
    async def refresh_callback(self, interaction: Interaction):  
        try:  
            r = await send_info_embed(self.player, interaction, if_send=False)  
            if r is None: return  
            eb, view = r  
            await interaction.response.edit_message(embed=eb, view=view)  
        except Exception as e:  
            await self.button_error(interaction, e)  
  
    async def volume_callback(self, interaction: Interaction):  
        try:  
            await interaction.response.send_message(  
                view=VolumeControlButtons(self.player),   
                ephemeral=True  
            )  
        except Exception as e:  
            await self.button_error(interaction, e)

    # @button(label='歌詞搜尋', emoji='🔍')
    # async def search_callback(self, interation: Interaction):
    #     try:
    #         await interation.response.defer(ephemeral=True, thinking=True)
    #         result = await self.player.search_lyrics()

    #         if len(result) > 2000:
    #             file = File(io.BytesIO(result.encode()), filename='lyrics.txt')
    #             result = result[:1996] + '...'
    #         else:
    #             file = None

    #         await interation.followup.send(result, **({'file': file} if file else {}), ephemeral=True) # type: ignore
    #     except Exception as e:
    #         await self.button_error(interation, e)

class VolumeControlButtons(View):
    def __init__(self, player: Player, timeout = 180):
        super().__init__(timeout=timeout)
        self.player = player

    @button(label='音量-50%', emoji='⏬')
    async def volume_down_50(self, interaction: Interaction, button: Button):
        try:
            await interaction.response.defer()
            await self.player.volume_adjust(reduce=0.5)
        except Exception as e:
            traceback.print_exc()

    @button(label='音量-10%', emoji='➖')
    async def volume_down_10(self, interaction: Interaction, button: Button):
        try:
            await interaction.response.defer()
            await self.player.volume_adjust(reduce=0.1)
        except Exception as e:
            traceback.print_exc()

    @button(label='正常音量', emoji='🔊')
    async def volume_normal(self, interaction: Interaction, button: Button):
        try:
            await interaction.response.defer()
            await self.player.volume_adjust(volume=1.0)
        except Exception as e:
            traceback.print_exc()

    @button(label='音量+10%', emoji='➕')
    async def volume_up_10(self, interaction: Interaction, button: Button):
        try:
            await interaction.response.defer()
            await self.player.volume_adjust(add=0.1)
        except Exception as e:
            traceback.print_exc()

    @button(label='音量+50%', emoji='🔼')
    async def volume_up_50(self, interaction: Interaction, button: Button):
        try:
            await interaction.response.defer()
            await self.player.volume_adjust(add=0.5)
        except Exception as e:
            traceback.print_exc()
