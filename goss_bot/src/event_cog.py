# goss_bot/src event_cog.py

import logging

from ..config import config, secret

import discord
import discord.ext.commands as dcmds
import discord_slash as dslash
import discord_slash.cog_ext as cog_ext

from .goss_cog_base import GossCogBase

class EventCog(GossCogBase):
    # Method called before regular command invoke
    @dcmds.Cog.listener()
    async def on_command(self, ctx: dcmds.Context):
        self.log.info(
            f"Command recieved: @{ctx.author} triggered '{ctx.command}' in #{ctx.channel} of '{ctx.guild}' with '{ctx.message.content}'")
    
    # Method called when a slash command is triggered
    @dcmds.Cog.listener()
    async def on_slash_command(self, ctx: dslash.SlashContext):
        self.log.info(f"Slash command recieved: @{ctx.author} triggered '{ctx.command}' in #{ctx.channel} of '{ctx.guild}'")