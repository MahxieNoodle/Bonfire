from discord.ext import commands
import discord

from . import utils

import asyncio


class Filters:
    """This class contains all the commands for custom filters"""

    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    @commands.guild_only()
    @utils.custom_perms(send_messages=True)
    @utils.check_restricted()
    async def filters(self, ctx):
        """Prints all the custom filters that this server currently has

        EXAMPLE: !filters
        RESULT: All filters setup on this server"""
        filters = self.bot.db.load('filters', key=ctx.message.guild.id, pluck='filters')
        if filters:
            entries = [t['filterName'] for t in filters]
            pages = utils.Pages(self.bot, message=ctx.message, entries=entries)
            await pages.paginate()
        else:
            await ctx.send("There are no filters setup on this server!")

    @commands.command()
    @commands.guild_only()
    @utils.custom_perms(send_messages=True)
    @utils.check_restricted()
    async def myfilters(self, ctx):
        """Prints all the custom filters that this server that you own

        EXAMPLE: !myfilters
        RESULT: All your filters setup on this server"""
        filters = self.bot.db.load('filters', key=ctx.message.guild.id, pluck='filters')
        if filters:
            entries = [t['filterName'] for t in filters if t['author'] == str(ctx.message.author.id)]
            if len(entries) == 0:
                await ctx.send("You have no filters setup on this server!")
            else:
                pages = utils.Pages(self.bot, message=ctx.message, entries=entries)
                await pages.paginate()
        else:
            await ctx.send("There are no filters setup on this server!")

 
    @commands.command()
    @commands.guild_only()
    @utils.custom_perms(manage_guild=True)
    @utils.check_restricted()
    async def filter(self, ctx, *options):
        """
        This is an intuitive command to restrict something to/from something
        The format is `!restrict what from/to who/where`

        For example, `!restrict command to role` will require a user to have `role`
        to be able to run `command`
        `!restrict command to channel` will only allow `command` to be ran in `channel`

        EXAMPLE: !restrict boop from @user
        RESULT: This user can no longer use the boop command
        """
        # First make sure we're given three options
        if len(options) >= 2:
            await ctx.send("You need to provide 2-3 options! Such as \n `add derpi 49372` \n or \n `remove e621`")
            return
        else:
            # Get the three arguments from this list, then make sure the 2nd is either from or to
            if len(options) < 2:
                arg3 = 0
                return
            else:
                arg1, arg2, arg3 = options

            if arg2.lower() not in ['derpi', 'e621']:
                await ctx.send("The 2nd option needs to be either \"derpi\" or \"e621\". Such as: `add derpi 49372` "
                               "or `add e621 tag,tag_name,tag`")
                return
            elif arg1.lower() not in ['add', 'remove']:
                await ctx.send("The 2nd option needs to be either \"add\" or \"delete\". Such as: `add derpi 49372` "
                               "or `remove e621`")
                return

        await ctx.send("I have just restricted {} {} {}".format(arg1, arg2, arg3))







def setup(bot):
    bot.add_cog(Filters(bot))
