import discord
import db
import time
from dateutil import parser
import calendar
bot = discord.Bot()
from discord.commands import Option

token = input("Please input your token:")
refreshTimeout = 4*86400
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
            embeds.add_field(name="Associated Website (County/Location)",value=deed['location'],inline=True)
            embeds.add_field(name="Date:", value=deed['date'],inline=True)
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
            embeds.add_field(name="Associated Website (County/Location)",value=deed['location'],inline=True)
            embeds.add_field(name="Date:", value=deed['date'],inline=True)
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

@bot.slash_command(guild_ids=[922599971461672961])
async def fetch_deeds_county(ctx, time: Option(str, "Time range. Format = 2022/2/20 2022/2/22",Required=True), county: Option(str,"County to look for"), price: Option(str,"Price Range. format: 250 30000",Required=False)):
    data = db.fetchDeedsInDesiredRangeAndCounty(calendar.timegm(parser.parse(time.split(" ")[0]).timetuple()) , calendar.timegm(parser.parse(time.split(" ")[1]).timetuple()),county=county, price=[int(price.split(" ")[0]),int(price.split(" ")[1])])
    for auction in range(len(data)):
        for deed in data[auction]:
            embeds = discord.Embed()
            embeds.add_field(name="Case Number:", value=deed['case_no'],inline=True)
            embeds.add_field(name="Opening Bid:", value=deed['opening_bid'],inline=True)
            embeds.add_field(name="Parcel URL:", value=deed['url'],inline=True)
            embeds.add_field(name="Property Address:", value=deed['property_address'],inline=True)
            embeds.add_field(name="Assessed Value:", value=deed['assessed_value'],inline=True)
            embeds.add_field(name="Associated Website (County/Location)",value=deed['location'],inline=True)
            embeds.add_field(name="Date:", value=deed['date'],inline=True)
            await ctx.send(embed=embeds)

@bot.slash_command(guild_ids=[922599971461672961])
async def set_timeout(ctx,timeout: Option(int,"Timeout of database refresh, recommended around every 4 days")):
    refreshTimeout=timeout
    await ctx.send(f"Set timeout to {timeout} days!")



@bot.event
async def notify(auction):
    channel = bot.get_channel(922599971461672964)
    embed =discord.Embed()
    embed.add_field(name='Date:', value= auction['date'])
    embed.add_field(name='Location:',value=auction['location'])
    embed.add_field(name='URL:',value=auction['url'])
    embed.add_field(name='Number of deeds:',value=len(auction['deeds']))
    await channel.send(embed=embed)
    await channel.send(f"@everyone, Auction with id {auction['_id']} will start in 15 minutes!, updating database!")
    time1= time.time()
    db.updateAuctionDB()
    time2=time.time()
    await channel.send(f"Database updated in {time2-time1} seconds, to see this auction, use this command: /check_auction_by_id {auction['_id']}")

async def main():
    auctions = db.fetchAllAuctions()
    while True:
        for auction in auctions:
            if auction['unixTimestamp'] <= time.time()-600:
                   pass
        
            else: 
                pass
        time.sleep(1)
bot.run(token)
        