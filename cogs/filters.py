import rethinkdb as r
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

from . import utils

import discord
import asyncio

class Filters:
    def __init__(self, bot):
        self.bot = bot

        @commands.command(aliases=['blocklist'])
        @utils.custom_perms(send_messages=True)
        @utils.check_restricted()
        async def blacklists(self, ctx):
            """Prints all blacklists and their tags for e621 and derpi.

            EXAMPLE: !blacklists
            RESULT: All blacklists for this server server"""
            #tags = self.bot.db.load('filters', key=str(ctx.guild.id), pluck='filters')
            await ctx.send("There are no tags setup on this server!")




def setup(bot):
    bot.add_cog(Filters(bot))