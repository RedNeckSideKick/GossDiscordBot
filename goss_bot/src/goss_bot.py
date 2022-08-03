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
from .admin_cog import AdminCog
from .management_cog import ManagementCog

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
        self.add_cog(AdminCog(self))
        self.add_cog(ManagementCog(self))

        return None

    # Bot stopping method, used for signal handling, etc.
    def _stop_bot(self, reason=None):
        self.log.info(f"Recieved request to stop bot: Reason = {reason}")
        self.exit_reason = reason
        self.loop.stop()

    # Bot start method
    def run(self):
        # if not self._context_managed:
        #     raise BotContextError("Please run this bot using a context manager")

        self.log.info("Starting bot...")
        self.exit_reason = None

        # Interupt signal handlers for asyncio loop - copied from discord.py Client.run()
        try:
            # Unlike normal signals, asyncio does not pass the signal or frame along
            self.loop.add_signal_handler(signal.SIGINT, lambda : self._stop_bot(f"SIGINT (Signum {signal.SIGINT})"))
            self.loop.add_signal_handler(signal.SIGTERM, lambda : self._stop_bot(f"SIGTERM (Signum {signal.SIGTERM})"))
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
                return self.exit_reason # Used in return result of starter future task, later returned from run()
        
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

        await self._update_owner_info()
        self.log.info(f"Owner user is {self.owner}")
        if self.owner is not None:
            await self.owner.send(f"{config.NAME} v{config.VERSION} connected at `{datetime.now()}`")
        else:
            self.log.warn("Unable to locate owner user. They won't recieve real-time updates from this bot!")

    # Method to collect owner information for authentication, ruggedized for future use
    async def _update_owner_info(self):
        self.log.info(f"Getting owner information from application info")
        self.app_info = await self.application_info()
        if self.app_info.team is not None:  # If bot is owned by a team
            self.log.debug("Extracting owners from team info")
            self.owner_id = self.app_info.team.owner_id
            # Technically you're not supposed to have both, however this lets us discriminate between team owner and team members
            self.owner_ids = set(tm.id for tm in self.app_info.team.members)
            self.owner = self.get_user(self.owner_id)
            self.owners = set(self.get_user(id) for id in self.owner_ids)
        else:   # Bot is individually owned
            self.log.debug("Extracting owners from individual info")
            self.owner_id = self.app_info.owner.id
            self.owner = self.app_info.owner

    # Method called just before closing connection, any last-words actions before logging off.
    async def before_close(self):
        if self.owner is not None:
            await self.owner.send(f"Disconnected at `{datetime.now()}` with exit reason `{self.exit_reason}`")
        await self.change_presence(status=discord.Status.idle, activity=discord.Game(name="Daisy_Bell.mp3"))
