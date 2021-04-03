# goss_bot/src goss_bot.py

import os
import signal
import logging
from datetime import datetime

from discord.ext.commands.core import before_invoke

# from configobj import ConfigObj

from ..config import config, secret

import asyncio
import discord
import discord.ext.commands as dcmds
import discord_slash as dslash

from .event_cog import EventCog
from .basic_cog import BasicCog

# Bot framework, derived from Discord bot class
class GossBot(dcmds.Bot):
    def __init__(self, path: os.path, **kwargs):
        # Initialize member variables
        self.path = path

        # Create logger
        self.log = logging.getLogger(self.__class__.__name__)

        # Initialize bot component
        self.log.info("Initializing bot")
        full_options = config.bot_options
        full_options["intents"]  = discord.Intents.default()    # Request default intents
        full_options["intents"].members = True  # Add member intents (this leaves just presences disabled)
        full_options["status"]   = status=discord.Status.idle
        full_options["activity"] = discord.Game(name="Starting up")
        super(GossBot, self).__init__(**full_options)

        # Initialize slash commands
        self.slash = dslash.SlashCommand(self, sync_commands=True)

        # Load functionality from Cogs
        # Base functionality Cogs always loaded
        self.add_cog(EventCog(self))
        self.add_cog(BasicCog(self))

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
                await self.start(secret.TOKEN)
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
        self.last_ready = datetime.now()
        self.log.info(f"Bot ready: signed in as {self.user} (id:{self.user.id})")

        # Change bot status to something useful
        await self.change_presence(activity=discord.Game(name="with the Discord API"))

        self.log.info("Getting owner information")
        self.app_info = await self.application_info()
        self.owner_user = self.app_info.owner
        if not self.owner_user.dm_channel:
            self.log.warn("Had to create DM with owner")
            await self.owner_user.create_dm()
        await self.owner_user.dm_channel.send(f"{config.NAME} v{config.VERSION} connected at `{datetime.now()}`")

    # Method called just before closing connection, any last-words actions before logging off.
    async def before_close(self):
        await self.owner_user.dm_channel.send(f"Disconnected at `{datetime.now()}`")
        await self.change_presence(status=discord.Status.idle, activity=discord.Game(name="Daisy_Bell.mp3"))
