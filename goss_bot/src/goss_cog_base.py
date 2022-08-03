# goss_bot/src goss_cog_base.py

import functools
import logging

import discord
import discord.ext.commands as dcmds
import discord_slash as dslash
import discord_slash.cog_ext as cog_ext

class GossCogBase(dcmds.Cog):
    # Initialize cog with a logger only when this class is subclassed
    def __init__(self, bot):
        if self.__class__ is GossCogBase:
            raise NotImplementedError("GossCogBase must be subclassed")
        
        self.bot = bot
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.info(f"Cog '{self.__class__.__name__}' initialized")
