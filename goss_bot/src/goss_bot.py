# goss_bot/src goss_bot.py

import os
import signal
import logging
from configobj import ConfigObj

import asyncio
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
        self.bot_intents = discord.Intents.default() # Request default intents
        self.bot_intents.members = True  # Add member intents (this leaves just presences disabled)
        super(GossBot, self).__init__(**self.config["Bot Options"], intents=self.bot_intents)

        return None

    # Entry/exit methods - modified from discord.py Client.run()
    async def _starter(self):
        await self.start(self.secret["token"])

    async def _stopper(self):
        await self.change_presence(status=discord.Status.idle, activity=discord.Game(name="Daisy_Bell.mp3"))
        await self.close()
    
    def _stop_loop_on_completion(self, f):
        self.loop.stop()

    # Context manager entry method
    def __enter__(self):
        self.log.debug("Entering context manager")
        self._context_managed = True

        # Interupt signal handlers for asyncio loop - copied from discord.py Client.run()
        try:
            self.loop.add_signal_handler(signal.SIGINT, lambda: self.loop.stop())
            self.loop.add_signal_handler(signal.SIGTERM, lambda: self.loop.stop())
        except NotImplementedError:
            pass
        # Add future for start method - modified from discord.py Client.run()
        self._starter_future = asyncio.ensure_future(self._starter(), loop=self.loop)
        self._starter_future.add_done_callback(self._stop_loop_on_completion)

        return self

    # Context manager exit method
    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            self.log.info(f"Exiting context manager with {exc_type, exc_value, traceback}")
        else:
            self.log.debug(f"Exiting context manager with {exc_type, exc_value, traceback}")

        if not self.is_closed():
            self.loop.run_until_complete(asyncio.ensure_future(self._stopper(), loop=self.loop))

        # Cleanup stuff - modified from discord.py Client.run()
        self._starter_future.remove_done_callback(self._stop_loop_on_completion)
        self.log.info('Cleaning up tasks.')
        discord.client._cleanup_loop(self.loop)

        if not self._starter_future.cancelled():
            try:
                return self._starter_future.result()
            except KeyboardInterrupt:
                # I am unsure why this gets raised here but suppress it anyway
                return None

        self._context_managed = False
        return None

    # Bot start method
    def run(self):
        if not self._context_managed:
            raise BotContextError("Please run this bot using a context manager")

        self.log.info("Running bot...")
        self.loop.run_forever() # Start asyncio loop - moved from try-except-finally in discord.py Client.run() to use context managers
        self.log.debug("run() exiting...")

    # Method called upon successful connection to Discord
    async def on_ready(self):
        self.log.info(f"Bot ready: signed in as {self.user} (id:{self.user.id})")
        self.log.info(f"I am a member of these guilds:\n{self.guilds}")

        # Change bot status to something useful
        await self.change_presence(activity=discord.Game(name="with the Discord API"))
