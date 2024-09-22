from utils.embed import embed
from nextcord.ext import commands
import nextcord, json
from typing import Optional


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.snipe_dict = {}

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, exception):
        if isinstance(exception, commands.CommandNotFound):
            return
        if ctx.cog != self:
            return
        await ctx.send(
            f"An error has occurred [{self.__class__.__name__} COG].\n{exception}"
        )

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        self.snipe_dict[message.channel.id] = [message.content, message.created_at, message.author]

    @commands.command()
    @commands.has_any_role(1274751694248480878, 1280220951077720178)  # 100m donor
    async def snipe(self, ctx):
        try:
            await ctx.send(
            embed=embed(
                "Sniped Message",
                description=f"{self.snipe_dict[ctx.channel.id][0]} \n{nextcord.utils.format_dt(self.snipe_dict[ctx.channel.id][1], "R")} sent by {self.snipe_dict[ctx.channel.id][2].mention}",
            )
        )
        except:
            await ctx.send("There's nothing to snipe!", delete_after=2)

    @commands.command(aliases=["pu"])
    @commands.has_any_role(1274079697684402237, 1280220951077720178)
    async def purge(self, ctx, limit: int):
        await ctx.channel.purge(limit=limit)
        await ctx.send(f"Purged {limit} messages.", delete_after=3)

    @commands.command(aliases=["uvl"])
    @commands.has_any_role(1275022893264404533, 1280220951077720178)
    async def unviewlock(self, ctx, role:Optional[nextcord.Role]):
        with open("config.json", "r") as config:
            config = json.load(config)
        await ctx.channel.set_permissions(
            role if role else ctx.guild.get_role(config["defaultrole"]),
            view_channel=True,
        )

        await ctx.channel.set_permissions(ctx.author, view_channel=True)
        await ctx.message.delete()
        await ctx.send("Done", delete_after=2)

    @commands.command(aliases=["vl"])
    @commands.has_any_role(1275022893264404533, 1280220951077720178)
    async def viewlock(self, ctx, role:Optional[nextcord.Role]):
        with open("config.json", "r") as config:
            config = json.load(config)
        await ctx.channel.set_permissions(
            role if role else ctx.guild.get_role(config["defaultrole"]),
            view_channel=False
            )
        await ctx.channel.set_permissions(ctx.guild.default_role, view_channel=False)
        await ctx.channel.set_permissions(ctx.author, view_channel=True)
        await ctx.message.delete()
        await ctx.send("Done", delete_after=2)

    @commands.command(aliases=["rvp"])
    @commands.has_any_role(1275022893264404533, 1280220951077720178)
    async def reset_channel_overwrites(self, ctx):
        channel = ctx.channel
        for overwrite_target in channel.overwrites:
            await channel.set_permissions(overwrite_target, overwrite=None)

        await ctx.send("Done")

    @commands.command(aliases=["akg"])
    @commands.has_any_role(1275022893264404533, 1280220951077720178)
    async def allow_grinder_view(self, ctx):
        channel = ctx.channel
        with open("config.json", "r") as config:
            config = json.load(config)
        await channel.set_permissions(
            ctx.guild.get_role(config["defaultrole"]), view_channel=False
        )
        await channel.set_permissions(ctx.guild.get_role(1275506029010096313), view_channel=True)
        await ctx.message.delete()
        await ctx.send("Done", delete_after=2)

def setup(bot):
    bot.add_cog(Utility(bot))
