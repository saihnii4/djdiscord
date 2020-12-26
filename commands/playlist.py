import time
import uuid

import discord
import discord.ext.commands
import discord.ext.menus

from utils.converters import NameValidator
from utils.converters import PlaylistConverter
from utils.converters import PlaylistPaginator
from utils.converters import PlaylistsPaginator
from utils.converters import SongConverter


@discord.ext.commands.group(name="playlist")
async def playlist(ctx: discord.ext.commands.Context) -> None:
    if ctx.invoked_subcommand is None:
        notif = (
            ctx.bot.templates.incompleteCmd.copy()
                .set_thumbnail(url="https://media4.giphy.com/media/TqiwHbFBaZ4ti/giphy.gif")
                .set_author(
                name=ctx.author.name, icon_url=ctx.author.avatar_url_as(format="png")
            )
            .set_footer(text="Unix Time: %d" % time.time())
        )
        notif.description = notif.description.format(ctx)
        return await ctx.send(embed=notif)

@playlist.command(name="delete")
async def delete(ctx: discord.ext.commands.Context) -> None:
    return await ctx.send("NotImplementedError: This command has not been implemented yet :p")


@playlist.command(name="list")
async def list(
    ctx: discord.ext.commands.Context, playlist: PlaylistConverter = None
) -> None:
    if playlist is None:
        playlists = [entry async for entry in await ctx.database.database.table("accounts").filter({"author": ctx.author.id}).run(ctx.database.connection)]
        paginator = discord.ext.menus.MenuPages(source=PlaylistsPaginator(ctx=ctx, playlists=playlists), clear_reactions_after=True)
        return await paginator.start(ctx)
    paginator = discord.ext.menus.MenuPages(source=PlaylistPaginator(
        playlist.songs, ctx=ctx, playlist=playlist), clear_reactions_after=True)
    await paginator.start(ctx)

@playlist.command(name="add")
async def add(
    ctx: discord.ext.commands.Context, playlist: PlaylistConverter, song: SongConverter
) -> None:
    message = ctx.bot.templates.playlistChange.copy()
    await playlist.add_song(ctx, song)
    return await ctx.send(
        embed=message.add_field(
            name="New Song!", value="%s {}".format(song.title) % song.emoji
        )
    )


@playlist.command(name="create")
async def create(ctx: discord.ext.commands.Context, *, playlist: NameValidator) -> None:
    playlist_id = str(uuid.uuid4())
    await ctx.database.database.table("accounts").insert(
        {
            "name": playlist,
            "id": playlist_id,
            "author": ctx.author.id,
            "songs": [],
            "cover": None,
        }
    ).run(ctx.database.connection)

    msg = await ctx.send(
        embed=discord.Embed(title="Almost there!", color=0xDA3E52).add_field(
            name="Cover Art",
            value="Now upload your cover art, if you don't want to upload anything, ignore this message for 10 seconds",
        ).set_image(url="https://res.cloudinary.com/practicaldev/image/fetch/s--0TbCN_Xq--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_66%2Cw_880/https://dev-to-uploads.s3.amazonaws.com/i/tb6tb1wvi7f00eqns3g0.gif"
    ))

    response = await ctx.wait_for(
        "message", check=lambda message: message.author == ctx.author, timeout=10
    )

    if response is None:
        return

    if not response.attachments:
        return await ctx.send(
            "You didn't send an attachment to set as your cover art, so we stopped listening"
        )

    await ctx.database.database.table("accounts").filter({"id": playlist_id}).update(
        {"cover": response.attachments[0].url}
    ).run(ctx.database.connection)

    return await msg.edit(
        embed=discord.Embed(
            title="All done!",
            description="Everything is clear! Begin adding songs to your playlist!",
            color=0xF2E94E)
        .add_field(name="Playlist Code", value=playlist_id)
        # .add_field(name="Song Limit", value="%d" % 40 if ctx.author.premium else 20)
        .set_thumbnail(url=response.attachments[0].url)
        .set_image(url="https://i.pinimg.com/originals/b9/88/b7/b988b7c3e84e1f83ef9447157831b460.gif"))

def setup(bot: discord.ext.commands.Bot) -> None:
    bot.add_command(playlist)
