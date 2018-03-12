from discord.ext import commands
import discord

from . import utils

import asyncio


class Filters:
    """This class contains all the commands for custom filtes/blacklists"""

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
        tags = self.bot.db.load('filters', key=ctx.message.guild.id, pluck='filters')
        if tags:
            entries = [t['trigger'] for t in tags]
            pages = utils.Pages(self.bot, message=ctx.message, entries=entries)
            await pages.paginate()
        else:
            await ctx.send("There are no filters setup on this server!")

    @commands.command()
    @commands.guild_only()
    @utils.custom_perms(send_messages=True)
    @utils.check_restricted()
    async def myfilters(self, ctx):
        """Prints all the custom tags that this server that you own

        EXAMPLE: !myfilters
        RESULT: All your tags setup on this server"""
        tags = self.bot.db.load('filters', key=ctx.message.guild.id, pluck='filters')
        if tags:
            entries = [t['trigger'] for t in tags if t['author'] == str(ctx.message.author.id)]
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
    async def filter(self, ctx, *, tag: str):
        """This can be used to call custom filters
        The format to call a custom tag is !filters <name>

        EXAMPLE: !filter e621
        RESULT: Whatever you setup for the e621 filter!!"""
        tag = tag.lower().strip()
        tags = self.bot.db.load('filters', key=ctx.message.guild.id, pluck='filters')
        if tags:
            for t in tags:
                if t['trigger'].lower().strip() == tag:
                    await ctx.send("\u200B{}".format(t['result']))
                    return
            await ctx.send("There is no filter called {}".format(tag))
        else:
            await ctx.send("There are no filters setup on this server!")

    @filter.command(name='add', aliases=['create', 'setup'])
    @commands.guild_only()
    @utils.custom_perms(send_messages=True)
    @utils.check_restricted()
    async def add_filter(self, ctx):
        """Use this to add a new filter that can be used in this server

        EXAMPLE: !filter add
        RESULT: A follow-along in order to create a new tag"""

        def check(m):
            return m.channel == ctx.message.channel and m.author == ctx.message.author and len(m.content) > 0

        my_msg = await ctx.send("Ready to setup a new filter! What do you want the name of for the filter to be?")

        try:
            msg = await self.bot.wait_for("message", check=check, timeout=60)
        except asyncio.TimeoutError:
            await ctx.send("You took too long!")
            return

        trigger = msg.content.lower().strip()
        forbidden_tags = ['add', 'create', 'setup', 'edit', '']
        if len(trigger) > 100:
            await ctx.send("Please keep filter names under 100 characters")
            return
        elif trigger in forbidden_tags:
            await ctx.send(
                "Sorry, but your filter name was detected to be forbidden. "
                "Current forbidden tag triggers are: \n{}".format("\n".join(forbidden_tags)))
            return

        tags = self.bot.db.load('filters', key=ctx.message.guild.id, pluck='filters') or []
        if tags:
            for t in tags:
                if t['trigger'].lower().strip() == trigger:
                    await ctx.send("There is already a filter setup called {}!".format(trigger))
                    return

        try:
            await my_msg.delete()
            await msg.delete()
        except (discord.Forbidden, discord.HTTPException):
            pass

        if trigger.lower() in ['edit', 'delete', 'remove', 'stop']:
            await ctx.send("You can't create a filter with {}!".format(trigger))
            return

        my_msg = await ctx.send(
            "Alright, your new filter can be called with {}!\n\nWhat do you want to be displayed with this filter?\n\n Please use a comma in between tags.".format(
                trigger))

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
        tag = {
            'author': str(ctx.message.author.id),
            'trigger': trigger,
            'result': result
        }
        tags.append(tag)
        entry = {
            'server_id': str(ctx.message.guild.id),
            'tags': tags
        }
        self.bot.db.save('tags', entry)
        await ctx.send("I have just setup a new tag for this server! You can call your tag with {}".format(trigger))

    @filter.command(name='edit')
    @commands.guild_only()
    @utils.custom_perms(send_messages=True)
    @utils.check_restricted()
    async def edit_filter(self, ctx, *, tag: str):
        """This will allow you to edit a tag that you have created
        EXAMPLE: !tag edit this tag
        RESULT: I'll ask what you want the new result to be"""
        tags = self.bot.db.load('tags', key=ctx.message.guild.id, pluck='tags')

        def check(m):
            return m.channel == ctx.message.channel and m.author == ctx.message.author and len(m.content) > 0

        if tags:
            for i, t in enumerate(tags):
                if t['trigger'] == tag:
                    if t['author'] == str(ctx.message.author.id):
                        my_msg = await ctx.send(
                            "Alright, what do you want the new result for the tag {} to be".format(tag))
                        try:
                            msg = await self.bot.wait_for("message", check=check, timeout=60)
                        except asyncio.TimeoutError:
                            await ctx.send("You took too long!")
                            return
                        new_tag = t.copy()
                        new_tag['result'] = msg.content
                        tags[i] = new_tag
                        try:
                            await my_msg.delete()
                            await msg.delete()
                        except discord.Forbidden:
                            pass
                        entry = {
                            'server_id': str(ctx.message.guild.id),
                            'tags': tags
                        }
                        self.bot.db.save('tags', entry)
                        await ctx.send("Alright, the tag {} has been updated".format(tag))
                        return
                    else:
                        await ctx.send("You can't edit someone else's tag!")
                        return
            await ctx.send("There isn't a tag called {}!".format(tag))
        else:
            await ctx.send("There are no tags setup on this server!")

    @filter.command(name='delete', aliases=['remove', 'stop'])
    @commands.guild_only()
    @utils.custom_perms(send_messages=True)
    @utils.check_restricted()
    async def del_filter(self, ctx, *, tag: str):
        """Use this to remove a tag from use for this server
        Format to delete a tag is !tag delete <tag>

        EXAMPLE: !tag delete stupid_tag
        RESULT: Deletes that stupid tag"""
        tags = self.bot.db.load('tags', key=ctx.message.guild.id, pluck='tags')
        if tags:
            for t in tags:
                if t['trigger'].lower().strip() == tag:
                    if ctx.message.author.permissions_in(ctx.message.channel).manage_guild or str(
                            ctx.message.author.id) == t['author']:
                        tags.remove(t)
                        entry = {
                            'server_id': str(ctx.message.guild.id),
                            'tags': tags
                        }
                        self.bot.db.save('tags', entry)
                        await ctx.send("I have just removed the tag {}".format(tag))
                    else:
                        await ctx.send("You don't own that tag! You can't remove it!")
                    return
        else:
            await ctx.send("There are no tags setup on this server!")


def setup(bot):
    bot.add_cog(Filters(bot))
