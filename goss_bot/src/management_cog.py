# goss_bot/src management_cog.py

import os
import logging
from datetime import datetime, timedelta
from discord import message

import gspread

from ..config import config, secret

import discord
import discord.ext.commands as dcmds
import discord_slash as dslash
import discord_slash.cog_ext as cog_ext

from .goss_cog_base import GossCogBase

class ManagementCog(GossCogBase):
    def __init__(self, bot):
        super().__init__(bot)
        self.log.info("Loading spreadsheet utilities. This may take a while...")
        import gspread
        self.log.info("Utilities loaded, logging into Google")
        self.gc = gspread.service_account(filename=secret.SRV_ACT_TOKEN_FILE)
        self.sh = self.gc.open(secret.SPREADSHEET_NAME)
        self.log.info("Spreadsheet opened")

        # Produce a dictionary of the available worksheets to access them easily by name
        self.wks = {}
        for wk in self.sh.worksheets():
            self.wks[wk.title] = wk
            # Get the names of all of the columns and store as a dictionary in a property to map colunm
            # names to numbers. Rows/columns also start at 1 like as shown on a spreadsheet. This of
            # course is confusing in the context considering, like most other programming languages,
            # Python indecies start at 0. Perhaps this is easier for you if you already have a lot of
            # MATLAB experince, lol.
            self.wks[wk.title].columns = {col: (colnum + 1) for colnum, col in enumerate(wk.row_values(1))}

        # self.sh.share("eqkessel@gmail.com", "user", "writer")

    # Help set up a member on the server
    @dcmds.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        self.log.info(f"New member @{member} joined the guild")
        try:
            found_name_cell = self.wks['Member Info'].find(str(member.id), in_column=self.wks["Member Info"].columns["User ID"])
            self.log.info(f"Member ID was already found on the spreadsheet, giving them roles back")

            # Give the user back their roles and update their nickname to their real name
            await self.update_member_from_spreadsheet(member, found_name_cell.row)

            # Send some information to the server too
            await self.notify_arrive_depart(member, "Member Rejoined the Server \N{Door}")

        except gspread.CellNotFound:    # ID was not found in the spreadsheet, must be new unregistered member
            self.log.info(f"User is a new or unregistered member")
            await member.send(f"""\
Welcome, Boilermaker! I am **{self.bot.user.name}**, the Goss Scholars Discord Server automation assistant!
To register yourself with my systems and get you set up on the server, please send me a message with _just_ your name __exactly as it \
appears on your student ID__. Thank you!""")
            self.wks["ID to Name"].append_row([str(member.id), False], table_range="A1") # Add their information to the next available row

    # Continued from above, when a direct message is detected
    @dcmds.Cog.listener()
    async def on_message(self, msg: discord.Message):
        if msg.channel.type is discord.ChannelType.private and msg.author is not self.bot.user:
            self.log.debug("Direct message received")
            try:
                found_id_cell = self.wks["ID to Name"].find(str(msg.author.id), in_column=self.wks["ID to Name"].columns["User ID"])

                # bool(str) == True, so a more direct check is needed                
                if self.wks["ID to Name"].cell(found_id_cell.row, self.wks["ID to Name"].columns["Registered"]).value != "TRUE":
                    self.log.info("Unregistered member responded to direct message")
                    try:
                        found_name_cell = self.wks["Member Info"].find(msg.content, in_column=self.wks["Member Info"].columns["Name"])
                        await msg.channel.send(f"Found you! Getting you registered now...")
                        self.log.info(f"Updating spreadsheet")
                        # Update spreadsheet
                        self.wks["Member Info"].update_cell(found_name_cell.row, self.wks["Member Info"].columns["User ID"], str(msg.author.id))
                        self.wks["Member Info"].update_cell(found_name_cell.row, self.wks["Member Info"].columns["User Profile"], f"@{msg.author}")
                        self.wks["ID to Name"].update_cell(found_id_cell.row, self.wks["ID to Name"].columns["Name"], msg.content)
                        self.wks["ID to Name"].update_cell(found_id_cell.row, self.wks["ID to Name"].columns["Registered"], True)
                        self.wks["ID to Name"].update_cell(found_id_cell.row, self.wks["ID to Name"].columns["User Profile"], f"@{msg.author}")

                        # Add membership role and set nickname
                        self.log.info(f"Applying roles and nickname")
                        guild = self.bot.get_guild(secret.guild_ids[0])
                        member = guild.get_member(msg.author.id)
                        await self.update_member_from_spreadsheet(member, found_name_cell.row, name=msg.content)

                        # Notify the new member of the success and give some info
                        await msg.channel.send(f"""\
Ok {msg.content}, you should be all set up now! I have taken the liberty to automatically set your server nickname to the name on your ID. \
If you would prefer a different nickname on the server, right click your profile on the server for the option, or use `/nick newname` in \
any channel to update it (remember to keep your prefered first name and last initial present).
If something is wrong, please message {self.bot.owner.mention} (my developer) ASAP to resolve the issue.
Thank you for getting set up, we're looking forward to seeing you on the server. Boiler Up!""")

                        # Send some information to the server too
                        await self.notify_arrive_depart(member, "Member Joined the Server \N{Door}")

                    except gspread.CellNotFound:    # Name not found on the spreadsheet
                        await msg.channel.send(f"""\
Sorry, I was unable to find a name `{msg.content}` to link your account with. Remember to enter your name _exactly_ as it appears on \
your student ID. Please try again.""")
            except gspread.CellNotFound:    # Somehow got a DM from someone who hasn't been recorded on the server
                self.log.warn("Direct message recieved from member with no record of joining server on spreadsheet")

    # Send notification when a member leaves
    @dcmds.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        self.log.info(f"Member {member} left the guild")
        await self.notify_arrive_depart(member, "Member Left the Server \N{Waving Hand Sign}", 0xff0000)

    # Method that sends a leave or join message in a system channel
    async def notify_arrive_depart(self, member: discord.Member, message: str, color=0x00ff00):
        embed = discord.Embed(color=color)
        embed.set_author(name=message, icon_url=str(member.avatar_url))
        embed.description = f"{member.mention}\n{member} ({member.id})"
        embed.set_footer(text=f"{member.guild.name} | {member.guild.member_count} members")
        await member.guild.system_channel.send(embed=embed)

    # Method to apply roles and nickname to a member
    async def update_member_from_spreadsheet(self, member: discord.Member, spreadsheet_row, name=None):
        guild = member.guild
        member_role = guild.get_role(secret.MEMBERSHIP_ROLE_ID)

        classnum = self.wks["Member Info"].cell(spreadsheet_row, self.wks["Member Info"].columns["Class"]).value
        advisor = self.wks["Member Info"].cell(spreadsheet_row, self.wks["Member Info"].columns["Advisor"]).value
        if name is None:
            name = self.wks["Member Info"].cell(spreadsheet_row, self.wks["Member Info"].columns["Name"]).value

        class_role = guild.get_role(secret.student_info_role_ids.get(classnum))
        advisor_role = guild.get_role(secret.student_info_role_ids.get(advisor))

        roles = [member_role]
        if class_role is not None:
            roles.append(class_role)
        else:
            self.log.warn(f"Error with getting class role (invalid class number {classnum})")
            await self.bot.owner.send(f"Error with getting class role for {member.mention} (invalid class number `{classnum}`)")
        if advisor_role is not None:
            roles.append(advisor_role)
        else:
            self.log.warn(f"Error with getting advisor role (invalid advisor {advisor})")
            await self.bot.owner.send(f"Error with getting advisor role for {member.mention} (invalid advisor `{advisor}`)")

        await member.edit(nick=name, roles=roles)
