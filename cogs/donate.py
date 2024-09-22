import nextcord
from nextcord.ext import commands
from nextcord import SlashOption
import cooldowns
from utils.embed import embed

gwmanager = 1277204324920983572
eventmanager = 1278012013448007703


class Donate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, exception):
        if isinstance(exception, commands.CommandNotFound):
            return
        if ctx.cog != self:
            return
        await ctx.send(
            f"An error has occurred [{self.__class__.__name__} COG].\n{exception}"
        )

    @nextcord.slash_command(name="dono")
    async def dono(self, interaction):
        return

    @dono.subcommand(name="giveaway")
    @cooldowns.cooldown(1, 10, bucket=cooldowns.SlashBucket.author)
    async def gw(
        self,
        interaction,
        prize: str = SlashOption(
            name="prize", description="What is the prize of your giveaway?"
        ),
        winners: int = SlashOption(
            name="winners", description="How many winners for your giveaway?"
        ),
        time: str = SlashOption(
            name="duration", description="How long do you want your giveaway to last?"
        ),
        req: str = SlashOption(
            name="requirement",
            description="Is there a requirement to enter the giveaway?",
            required=False,
        ),
        msg: str = SlashOption(
            name="message",
            description="Do you have a message for the giveaway?",
            required=False,
        ),
    ):
        ping = interaction.guild.get_role(gwmanager)
        await interaction.response.send_message(
            content=ping.mention,
            embed=embed(
                "Giveaway Donation",
                f"**Prize:** {prize}\n**Winners:** {winners}\n**Duration:** {time}\n**Requirement:** {req}\n**Message:** {msg}",
            ),
            allowed_mentions=nextcord.AllowedMentions.all(),
        )

    @dono.subcommand(name="event")
    @cooldowns.cooldown(1, 10, bucket=cooldowns.SlashBucket.author)
    async def event(
        self,
        interaction,
        prize: str = SlashOption(
            name="prize", description="What is the prize of the event?"
        ),
        event: int = SlashOption(
            name="event",
            description="What event do you want to donate for?",
            choices={
                "rumble": 1,
                "blacktea": 2,
                "bingo": 3,
                "mafia": 4,
                "hangry": 5,
            },
        ),
        note: str = SlashOption(
            name="note",
            description="Is there any requirements? Is there anything staff need to know?",
            required=False,
        ),
    ):
        dict = {
            1: "rumble",
            2: "blacktea",
            3: "bingo",
            4: "mafia",
            5: "hangry",
        }
        ping = interaction.guild.get_role(eventmanager)
        await interaction.response.send_message(
            content=ping.mention,
            embed=embed(
                "Event Donation",
                f"**Prize:** {prize}\n**Event:** {dict.get(event)}\n**Note:** {note}",
            ),
            allowed_mentions=nextcord.AllowedMentions.all(),
        )


def setup(bot):
    bot.add_cog(Donate(bot))
