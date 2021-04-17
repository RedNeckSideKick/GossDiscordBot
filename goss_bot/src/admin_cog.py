# goss_bot/src admin_cog.py

import logging
from datetime import datetime, timedelta

from ..config import config, secret

import discord
import discord.ext.commands as dcmds
import discord_slash as dslash
import discord_slash.cog_ext as cog_ext

from .goss_cog_base import GossCogBase

class AdminCog(GossCogBase):
    async def cog_check(self, ctx: dcmds.Context):
        self.log.info("Checking permissions for admin command")
        authenticated = False
        if await self.bot.is_owner(ctx.author):
            authenticated = True
        else:
            self.log.warn(f"Unauthorized access to admin command by @{ctx.author}")
        return authenticated

    @dcmds.command(name='admintest')
    async def _admintest(self, ctx: dcmds.Context, raise_exec=None):
        await ctx.reply(f"Admin authentication successful, greetings, {ctx.author.mention}.")
        if raise_exec:
            raise Exception(f"Test exception: {raise_exec}") # Testing exception handling