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

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    @utils.custom_perms(send_messages=True)
    @utils.check_restricted()
    async def filter(self, ctx, *, filter: str):
        """This can be used to call custom filters
        The format to call a custom filter is !filter <filter>

        EXAMPLE: !filter butts
        RESULT: Whatever you setup for the butts filter!!"""
        filter = filter.lower().strip()
        filters = self.bot.db.load('filters', key=ctx.message.guild.id, pluck='filters')
        if filters:
            for t in filters:
                if t['filterName'].lower().strip() == filter:
                    await ctx.send("\u200B{}".format(t['result']))
                    return
            await ctx.send("There is no filter called {}".format(filter))
        else:
            await ctx.send("There are no filters setup on this server!")

    @filter.command(name='add', aliases=['create', 'setup'])
    @commands.guild_only()
    @utils.custom_perms(send_messages=True)
    @utils.check_restricted()
    async def add_filter(self, ctx):
        """Use this to add a new filter that can be used in this server

        EXAMPLE: !filter add
        RESULT: A follow-along in order to create a new filter"""

        def check(m):
            return m.channel == ctx.message.channel and m.author == ctx.message.author and len(m.content) > 0

        my_msg = await ctx.send("Ready to setup a new filter! What do you want the filterName for the filter to be?")

        try:
            msg = await self.bot.wait_for("message", check=check, timeout=60)
        except asyncio.TimeoutError:
            await ctx.send("You took too long!")
            return

        filterName = msg.content.lower().strip()
        forbidden_filters = ['add', 'create', 'setup', 'edit', '']
        if len(filterName) > 100:
            await ctx.send("Please keep filter filterNames under 100 characters")
            return
        elif filterName in forbidden_filters:
            await ctx.send(
                "Sorry, but your filter filterName was detected to be forbidden. "
                "Current forbidden filter filterNames are: \n{}".format("\n".join(forbidden_filters)))
            return

        filters = self.bot.db.load('filters', key=ctx.message.guild.id, pluck='filters') or []
        if filters:
            for t in filters:
                if t['filterName'].lower().strip() == filterName:
                    await ctx.send("There is already a filter setup called {}!".format(filterName))
                    return

        try:
            await my_msg.delete()
            await msg.delete()
        except (discord.Forbidden, discord.HTTPException):
            pass

        if filterName.lower() in ['edit', 'delete', 'remove', 'stop']:
            await ctx.send("You can't create a filter with {}!".format(filterName))
            return

        my_msg = await ctx.send(
            "Alright, your new filter can be called with {}!\n\nWhat do you want to be displayed with this filter?".format(
                filterName))

        try:
            msg = await self.bot.wait_for("message", check=check, timeout=60)
        except asyncio.TimeoutError:
            await ctx.send("You took too long!")
            return

        result = msg.content
        try:
            await my_msg.delete()
            await msg.delete()
        except (discord.Forbidden, discord.HTTPException):
            pass

        # The different DB settings
        filter = {
            'author': str(ctx.message.author.id),
            'filterName': filterName,
            'result': result
        }
        filters.append(filter)
        entry = {
            'server_id': str(ctx.message.guild.id),
            'filters': filters
        }
        self.bot.db.save('filters', entry)
        await ctx.send("I have just setup a new filter for this server! You can call your filter with {}".format(filterName))

    @filter.command(name='edit')
    @commands.guild_only()
    @utils.custom_perms(send_messages=True)
    @utils.check_restricted()
    async def edit_filter(self, ctx, *, filter: str):
        """This will allow you to edit a filter that you have created
        EXAMPLE: !filter edit this filter
        RESULT: I'll ask what you want the new result to be"""
        filters = self.bot.db.load('filters', key=ctx.message.guild.id, pluck='filters')

        def check(m):
            return m.channel == ctx.message.channel and m.author == ctx.message.author and len(m.content) > 0

        if filters:
            for i, t in enumerate(filters):
                if t['filterName'] == filter:
                    if t['author'] == str(ctx.message.author.id):
                        my_msg = await ctx.send(
                            "Alright, what do you want the new result for the filter {} to be".format(filter))
                        try:
                            msg = await self.bot.wait_for("message", check=check, timeout=60)
                        except asyncio.TimeoutError:
                            await ctx.send("You took too long!")
                            return
                        new_filter = t.copy()
                        new_filter['result'] = msg.content
                        filters[i] = new_filter
                        try:
                            await my_msg.delete()
                            await msg.delete()
                        except discord.Forbidden:
                            pass
                        entry = {
                            'server_id': str(ctx.message.guild.id),
                            'filters': filters
                        }
                        self.bot.db.save('filters', entry)
                        await ctx.send("Alright, the filter {} has been updated".format(filter))
                        return
                    else:
                        await ctx.send("You can't edit someone else's filter!")
                        return
            await ctx.send("There isn't a filter called {}!".format(filter))
        else:
            await ctx.send("There are no filters setup on this server!")

    @filter.command(name='delete', aliases=['remove', 'stop'])
    @commands.guild_only()
    @utils.custom_perms(send_messages=True)
    @utils.check_restricted()
    async def del_filter(self, ctx, *, filter: str):
        """Use this to remove a filter from use for this server
        Format to delete a filter is !filter delete <filter>

        EXAMPLE: !filter delete stupid_filter
        RESULT: Deletes that stupid filter"""
        filters = self.bot.db.load('filters', key=ctx.message.guild.id, pluck='filters')
        if filters:
            for t in filters:
                if t['filterName'].lower().strip() == filter:
                    if ctx.message.author.permissions_in(ctx.message.channel).manage_guild or str(
                            ctx.message.author.id) == t['author']:
                        filters.remove(t)
                        entry = {
                            'server_id': str(ctx.message.guild.id),
                            'filters': filters
                        }
                        self.bot.db.save('filters', entry)
                        await ctx.send("I have just removed the filter {}".format(filter))
                    else:
                        await ctx.send("You don't own that filter! You can't remove it!")
                    return
        else:
            await ctx.send("There are no filters setup on this server!")


def setup(bot):
    bot.add_cog(Filters(bot))
