import nextcord


def embed(title, description, color=0x00FF00, footer=None):
    embed = nextcord.Embed(title=title, description=description, color=color)
    embed.set_footer(
        text=f"{'Rich Dankers' if not footer else footer}",
        icon_url="https://cdn.discordapp.com/icons/1274056217010114600/02fa9ffc0af770f388f783b995cadb10.webp?size=1024",
    )
    return embed
