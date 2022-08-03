# goss_bot/src base_cog.py

import logging
from datetime import datetime, timedelta

from ..config import config, secret

import discord
import discord.ext.commands as dcmds
import discord_slash as dslash
import discord_slash.cog_ext as cog_ext

from .goss_cog_base import GossCogBase

def hms_timedelta(timedelta: timedelta):
    s = timedelta.total_seconds()
    return f"{s//3600:02.0f}h {(s // 60) % 60:02.0f}m {s % 60:02.0f}s"

class BasicCog(GossCogBase):
    @cog_ext.cog_slash(name="ping", description="Check bot latency.", guild_ids=secret.guild_ids)
    async def _ping(self, ctx: dslash.SlashContext):
        await ctx.send(f"Pong! Client latency is `{self.bot.latency * 1000:.2f}ms`")

    @cog_ext.cog_slash(name="info", description="Get information about this bot.", guild_ids=secret.guild_ids)
    async def _info(self, ctx: dslash.SlashContext):
        embed = discord.Embed(title=f"{config.NAME} - v{config.VERSION}", description=self.bot.description)
        embed.add_field(name="Developer", value=config.DEVELOPER, inline=True)
        embed.add_field(name="Email", value=config.EMAIL, inline=True)
        embed.add_field(name="Profile", value=f"@{self.bot.owner}", inline=True)
        embed.add_field(name="Github", value=f"[{config.REPO}]({config.REPO})", inline=False)
        embed.add_field(name="Uptime", value=hms_timedelta(datetime.now() - self.bot.last_ready), inline=True)
        embed.add_field(name="Latency", value=f"{self.bot.latency * 1000:.2f}ms", inline=True)
        embed.set_thumbnail(url=str(self.bot.user.avatar_url))
        await ctx.send(embed=embed)
        