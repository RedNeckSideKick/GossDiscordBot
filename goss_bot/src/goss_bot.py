# goss_bot/src goss_bot.py

import os
import signal
import logging
from configobj import ConfigObj

import asyncio
import discord
import discord.ext.commands as dcmds

# Bot framework, derived from Discord bot class
class GossBot(dcmds.Bot):
    def __init__(self, config: ConfigObj, secret: ConfigObj, path: os.path, **kwargs):
        # Initialize member variables
        self.config = config
        self.secret = secret
        self.path = path

        # Create logger
        self.log = logging.getLogger(__name__.split('.')[-1])

        # Initialize bot component
        self.log.info("Initializing bot")
        self.bot_intents = discord.Intents.default() # Request default intents
        self.bot_intents.members = True  # Add member intents (this leaves just presences disabled)
        super(GossBot, self).__init__(**self.config["Bot Options"], intents=self.bot_intents)

        return None

    # Bot start method
    def run(self):
        # if not self._context_managed:
        #     raise BotContextError("Please run this bot using a context manager")

        self.log.info("Starting bot...")

        # Signal handler
        def handle_signal(signum):
            self.log.info(f"Intercepted signal (SIGNUM {signum}), stopping loop.")
            self.loop.stop()

        # Interupt signal handlers for asyncio loop - copied from discord.py Client.run()
        try:
            # Unlike normal signals, asyncio does not pass the signal or frame along
            self.loop.add_signal_handler(signal.SIGINT, lambda : handle_signal(signal.SIGINT))
            self.loop.add_signal_handler(signal.SIGTERM, lambda : handle_signal(signal.SIGTERM))
        except NotImplementedError as e:
            self.log.warn(f"Issue establishing signal handling for asyncio event loop, {e}")

        # Runner/completion methods - modified from discord.py Client.run()
        async def runner():
            try:
                self.log.info(f"Establishing connection and logging in.")
                await self.start(self.secret["token"])
            finally:
                if not self.is_closed():
                    self.log.info("Logging out and closing connection.")
                    await self.before_close()
                    await self.close()
        
        def stop_loop_on_completion(future):
            self.log.warn("Future completed, stopping loop.")
            self.loop.stop()

        # Add future for run method - modified from discord.py Client.run()
        starter_future = asyncio.ensure_future(runner(), loop=self.loop)
        starter_future.add_done_callback(stop_loop_on_completion)

        try:
            self.loop.run_forever() # Start asyncio loop - moved from try-except-finally in discord.py Client.run() to use context managers
        except KeyboardInterrupt as e:
            self.log.warn(f"Received {e}, terminating bot and event loop.")
        finally:
            starter_future.remove_done_callback(stop_loop_on_completion)
            self.log.info('Cleaning up tasks.')
            discord.client._cleanup_loop(self.loop)

        self.log.info("Bot has been shut down.")
        if not starter_future.cancelled():
            try:
                return starter_future.result()
            except KeyboardInterrupt as e:
                # Original devs unsure why this gets raised here but suppress it anyway
                return e

    # Method called upon successful connection to Discord
    async def on_ready(self):
        self.log.info(f"Bot ready: signed in as {self.user} (id:{self.user.id})")
        self.log.info(f"I am a member of these guilds:\n{self.guilds}")

        # Change bot status to something useful
        await self.change_presence(activity=discord.Game(name="with the Discord API"))

    # Method called just before closing connection, any last-words actions before logging off.
    async def before_close(self):
        await self.change_presence(status=discord.Status.idle, activity=discord.Game(name="Daisy_Bell.mp3"))
