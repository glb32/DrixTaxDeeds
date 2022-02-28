import discord
import db
import time
from dateutil import parser
import calendar
bot = discord.Bot()
from discord.commands import Option
token = input("Please input your token:")
@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

@bot.slash_command(guild_ids=[922599971461672961])
async def fetch_deeds_by_date_and_price(ctx, time: Option(str, "Time range. Format = 2022/2/20 2022/2/22",Required=True),price: Option(str,"Price Range. format: 250 30000",Required=False)):
    data = db.fetchDeedsInDesiredRange(calendar.timegm(parser.parse(time.split(" ")[0]).timetuple()) , calendar.timegm(parser.parse(time.split(" ")[1]).timetuple()), [int(price.split(" ")[0]),int(price.split(" ")[1])])
    for auction in range(len(data)):
        for deed in data[auction]:
            embeds = discord.Embed()
            embeds.add_field(name="Case Number:", value=deed['case_no'],inline=True)
            embeds.add_field(name="Opening Bid:", value=deed['opening_bid'],inline=True)
            embeds.add_field(name="Parcel URL:", value=deed['url'],inline=True)
            embeds.add_field(name="Property Address:", value=deed['property_address'],inline=True)
            embeds.add_field(name="Assessed Value:", value=deed['assessed_value'],inline=True)
            #embeds.add_field(name="Associated Website (County/Location)",value=data[auction]['location'])
            await ctx.send(embed=embeds)

@bot.slash_command(guild_ids=[922599971461672961])
async def fetch_deeds_by_county(ctx,county: Option(str,"County",Required=True)):
    data = db.fetchDeedsByCounty(county)
    for auction in range(len(data)):
        for deed in data[auction]:
            embeds = discord.Embed()
            embeds.add_field(name="Case Number:", value=deed['case_no'],inline=True)
            embeds.add_field(name="Opening Bid:", value=deed['opening_bid'],inline=True)
            embeds.add_field(name="Parcel URL:", value=deed['url'],inline=True)
            embeds.add_field(name="Property Address:", value=deed['property_address'],inline=True)
            embeds.add_field(name="Assessed Value:", value=deed['assessed_value'],inline=True)
            #embeds.add_field(name="Associated Website (County/Location)",value=data[auction]['location'],inline=True)
            await ctx.send(embed=embeds)

@bot.slash_command(guild_ids=[922599971461672961])
async def auctions_30_day_range(ctx):
    auctions = db.fetchNearestAuctions(time.time(),time.time()+2592000) #30-day range
    auctions = sorted(auctions,key=lambda x:len(x['deeds']))
    for auction in range(len(auctions)):
        embed= discord.Embed()
        embed.add_field(name="Date:", value=auctions[auction]['date'],inline=True)
        embed.add_field(name="Location:", value=auctions[auction]['location'],inline=True)
        embed.add_field(name="Auction URL:", value=auctions[auction]['url'],inline=True)
        embed.add_field(name="Total Number of Deeds", value=str(len(auctions[auction]['deeds'])),inline=True)
        await ctx.send(embed=embed)
bot.run(token)