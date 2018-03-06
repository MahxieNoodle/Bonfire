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
    @commands.guild_only()
    @utils.custom_perms(send_messages=True)
    @utils.check_restricted()
    async def blacklists(self, ctx, user = None):
        """Makes me hug a person!

        EXAMPLE: !hug @Someone
        RESULT: I hug the shit out of that person"""
        if user is None:
            user = ctx.message.author
        else:
            converter = commands.converter.MemberConverter()
            try:
                user = await converter.convert(ctx, user)
            except commands.converter.BadArgument:
                await ctx.send("Error: Could not find user: {}".format(user))
                return


def setup(bot):
    bot.add_cog(Filters(bot))