import discord
import db
bot = discord.Bot()


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

@bot.slash_command(guild_ids=[618048657001938974])
async def hello(ctx):
    await ctx.respond("Hello!")



bot.run("OTMyMDE2MzM1OTY0MjI1NTk3.YeM12g.WOiixyVSEy60NchY-7652IhVscY")