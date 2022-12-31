import discord
import wavelink

from discord.ext import commands 


bot = commands.Bot(command_prefix="!", intents=discord.Intents.all(), )
bot.remove_command('help')

songs_queue = wavelink.Queue()
skip_votes = []

class MusicPlayer(wavelink.Player):
    def __init__(self):
        super().__init__()


@bot.event
async def on_ready():
    bot.loop.create_task(connect_nodes())
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(f'Created By Moishale'))

async def connect_nodes():
    await bot.wait_until_ready()
    await wavelink.NodePool.create_node(
        bot=bot,
        host='127.0.0.1',
        port=2333,
        password='youshallnotpass'
    )

@bot.event
async def on_wavelink_node_ready(node: wavelink.Node):
    print(f'Node: <{node.identifier}> is ready!')

@bot.event
async def on_wavelink_track_end(player: MusicPlayer, track: wavelink.Track, reason):
        if not songs_queue.is_empty:
            next_song = songs_queue.get()
            await player.play(next_song)
        else:
            await player.disconnect()


@bot.command(aliases=['p'])
async def play(ctx: commands.Context, *, search: wavelink.YouTubeTrack):
        if not ctx.voice_client:
            vc: MusicPlayer = await ctx.author.voice.channel.connect(cls=MusicPlayer())
        else:
            vc: MusicPlayer = ctx.voice_client

        await vc.play(search)
        embed  = discord.Embed(title='Playing Song', color=discord.Colour.random())
        embed.set_thumbnail(url=f'{search.thumbnail}')
        embed.add_field(name='Song', value=f'{search}')
        embed.add_field(name='Duration', value=f'{round(search.duration/60, 2)}m')
        embed.set_footer(text=f'{ctx.author}', icon_url=f'{ctx.author.display_avatar}')
        await ctx.send(embed=embed)

@bot.command(aliases=['q'])
async def queue(ctx: commands.Context, *, search: wavelink.YouTubeTrack, ):
    songs_queue.put(search)
    
    embed  = discord.Embed(title='Added to the queue', color=discord.Colour.random())
    embed.set_thumbnail(url=f'{search.thumbnail}')
    embed.add_field(name='Song', value=f'{search}')
    embed.add_field(name='Duration', value=f'{round(search.duration/60, 2)}m')
    embed.set_footer(text=f'{ctx.author}', icon_url=f'{ctx.author.display_avatar}')
    await ctx.send(embed=embed)

@bot.command(aliases=['dq'])
async def display_queue(ctx: commands.Context):
    embed = discord.Embed(title='Queue', color=discord.Colour.blue())
    if songs_queue.is_empty: 
            await ctx.send(embed=discord.Embed(
                title='Queue is empty',
                description='Add songs to the queue!', 
            ))
    if not songs_queue.is_empty:
        for val,song in enumerate(songs_queue):
            embed.add_field(name=f'{val+1}', value=f'{song}' , inline=False)
        await ctx.send(embed=embed)

@bot.command(aliases=['s'])
async def skip(ctx: commands.Context):
    try:
        vc: MusicPlayer = ctx.voice_client
        if not vc.is_playing:
            await ctx.send(embed=discord.Embed(
                title='Not playing any music right now...',
                color=discord.Colour.random(),
            ))

        voter = ctx.message.author
        if voter.id not in skip_votes:
            skip_votes.append(voter.id)
            total_votes = len(skip_votes)

            if total_votes >= 2:
                await vc.stop()
                skip_votes.clear()
            else:
                await ctx.send(embed=discord.Embed(
                title=f'Skip vote added, currently at **{total_votes}/2**.',
                color=discord.Colour.random()
            ))

        else:
            await ctx.send(embed=discord.Embed(
                title='You have already voted to skip this song.',
                color=discord.Colour.random()
            ))
    except:
        await ctx.send(embed=discord.Embed(
            description='You are not in a VC.',
            color=discord.Colour.random(),
        ))

@bot.command(aliases=['d', 'dis'])
async def disconnect(ctx: commands.Context):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
    else:
        await ctx.send(embed=discord.Embed(
            title= 'Message!',
            description='The bot is not connected to a voice channel.',
            color=discord.Colour.random(),
        ))

@bot.command(aliases=['c', 'con'])
async def connect(ctx: commands.Context):
    try:
        channel = ctx.author.voice.channel
    except AttributeError:
        return await ctx.send(embed=discord.Embed(
            title= 'Message!',
            description='Please join a voice channel to connect.',
            color=discord.Colour.random(),
        ))

    if not ctx.voice_client:
        await ctx.author.voice.channel.connect(cls=MusicPlayer())
    else:
        await ctx.send(embed=discord.Embed(
            title= 'Message!',
            description='The bot is already connected to a voice channel.',
            color=discord.Colour.random(),
        ))

@bot.command(aliases=['pa'])
async def pause(ctx: commands.Context):
    try:
        vc: MusicPlayer = ctx.voice_client
        if not vc.is_playing:
            await ctx.send(embed=discord.Embed(
                title='Not playing any music right now...',
                color=discord.Colour.random(),
            ))
        else:
            await vc.pause()
            await ctx.message.add_reaction('⏸️')

    except:
        await ctx.send(embed=discord.Embed(
            title='You are not in a VC.',
            color=discord.Colour.random(),
        ))

@bot.command(aliases=['r'])
async def resume(ctx: commands.Context):
    try:
        vc: MusicPlayer = ctx.voice_client
        if not vc.is_playing:
            await ctx.send(embed=discord.Embed(
                title='Not playing any music right now...',
                color=discord.Colour.random(),
            ))
        else:
            await vc.resume()
            await ctx.message.add_reaction('▶️')

    except:
        await ctx.send(embed=discord.Embed(
            title='You are not in a VC.',
            color=discord.Colour.random(),
        ))


bot.run('Your_Token')
