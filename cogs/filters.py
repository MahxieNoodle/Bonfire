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
        async def filters(self, ctx):
            """Prints all the custom tags that this server currently has

            EXAMPLE: !tags
            RESULT: All tags setup on this server"""
            tags = self.bot.db.load('tags', key=ctx.message.guild.id, pluck='tags')
            if tags:
                entries = [t['trigger'] for t in tags]
                pages = utils.Pages(self.bot, message=ctx.message, entries=entries)
                await pages.paginate()
            else:
                await ctx.send("There are no tags setup on this server!")

def setup(bot):
    bot.add_cog(Filters(bot))
