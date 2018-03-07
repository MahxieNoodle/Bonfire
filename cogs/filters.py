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
            """Prints all blacklists and their tags for e621 and derpi.

            EXAMPLE: !blacklists
            RESULT: All blacklists for this server server"""
            tags = self.bot.db.load('filters', key=ctx.guild.id, pluck='filters')
            if tags:
                entries = [t['trigger'] for t in blacklists]
                pages = utils.Pages(self.bot, message=ctx.message, entries=entries)
                await pages.paginate()
            else:
                await ctx.send("There are no tags setup on this server!")
                return

def setup(bot):
    bot.add_cog(Filters(bot))
