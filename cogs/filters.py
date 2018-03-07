import rethinkdb as r
from discord.ext import commands
import discord

from . import utils

import asyncio


class Filters:

    def __init__(self, bot):
        self.bot = bot

        @commands.command()
        @commands.guild_only()
        @utils.custom_perms(send_messages=True)
        @utils.check_restricted()
        async def blacklists(self, ctx):

            await ctx.send("There are no tags setup on this server!")
            return

def setup(bot):
    bot.add_cog(Filters(bot))
