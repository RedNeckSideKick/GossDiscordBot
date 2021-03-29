# goss_bot/src goss_bot.py

import os
import logging
from configobj import ConfigObj

import discord
import discord.ext.commands as dcmds

class BotBaseError(Exception):
    pass

class BotContextError(BotBaseError):
    pass

# Bot framework, derived from Discord bot class
class GossBot(dcmds.Bot):
    def __init__(self, config: ConfigObj, secret: ConfigObj, path: os.path, **kwargs):
        # Initialize member variables
        self._context_managed = False
        self.config = config
        self.secret = secret
        self.path = path

        # Create logger
        self.log = logging.getLogger("GossBot")

        # Initialize bot component
        self.log.info("Initializing bot")
        self.bot_intents = discord.Intents.all()    # Request all intents. May be inefficient but easy for now
        super(GossBot, self).__init__(**self.config["Bot Options"], intents=self.bot_intents)

        return None

    # Context manager entry method
    def __enter__(self):
        self.log.debug("Entering context manager")
        self._context_managed = True
        return self

    # Context manager exit method
    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            self.log.info(f"Exiting context manager with {exc_type, exc_value, traceback}")
        else:
            self.log.debug(f"Exiting context manager with {exc_type, exc_value, traceback}")
        self._context_managed = False
        return None

    # Bot start method
    def run(self):
        if not self._context_managed:
            raise BotContextError("Please run this bot using a context manager")

        self.log.info("Running bot...")
        super(GossBot, self).run(self.secret["token"])
        self.log.debug("run() exiting...")

    # Method called upon successful connection to Discord
    async def on_ready(self):
        self.log.info(f"Bot ready: signed in as {self.user} (id:{self.user.id})")
        self.log.info(f"I am a member of these guilds:\n{self.guilds}")

        # Change bot status to something useful
        await self.change_presence(activity=discord.Game(name="with the Discord API"))
