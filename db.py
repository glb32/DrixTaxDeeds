from distutils.command.build import build
import pymongo
from scraping import url_scraper,deed_scraper
from urllib.parse import urlparse
client=pymongo.MongoClient("mongodb+srv://admin:admin@cluster0.goify.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
base = client.DrixTaxDeeds


'''
buildSiteDB()
@param:
state = int (0,3)
see definition of getAllUrlsPerState()

@desc:
organizes tax deed and foreclosure site urls into mongoDB database 
'''
def buildSiteDB(state):
    base.Taxdeeds.delete_many({})
    base.Foreclosures.delete_many({})
    sites=url_scraper.getAllUrlsPerState(state)
    for key in sites:
        if key['isTaxdeed'] == True:
            base.Taxdeeds.insert_one(key)
        if key['isTaxdeed'] == False:
            base.Foreclosures.insert_one(key)
        if key['isTaxdeed'] == None:
            base.Taxdeeds.insert_one(key)
            base.Foreclosures.insert_one(key)
            

def updateAuctionDB(foreclosure=False):
    SiteObjects = []
    auctions = []
    for x in base.Taxdeeds.find({}):
        SiteObjects.append(x)
    auctions = url_scraper.getAuctionsPerCounty(SiteObjects)
    for auction in auctions:
        auction['deeds'] = deed_scraper.parseDeeds(auction['url'])

    client.DrixTaxDeeds.Auctions.delete_many({})
    client.DrixTaxDeeds.Auctions.insert_many(auctions)


def extractDeeds(auction):
    return auction['deeds']

def fetchAuctionsInDesiredRange(date1,date2,price=None):
    auctions=client.DrixTaxDeeds.Auctions.find({"unixTimestamp":{"$gte":date1,"$lte":date2}})
    arr=[]
    for auction in auctions:
        arr.append(extractDeeds(auction))
    if price is None:
        pass
    else:
        for auction in arr:
            for deed in auction:
                if deed['assessed_value'] >= price[0]: 
                    if deed['assessed_value'] <= price[1]: 
                        pass
                else:
                    auction.remove(deed)
            auction = sorted(auction,key=lambda x: x['assessed_value'])

        
    with open('auctions.json','w+') as f:
        f.write(str(arr))
    return arr, str(f"Fetched deeds in price range:{price[0]}-{price[1]} USD, and in date range {date1}-{date2}" )

fetchAuctionsInDesiredRange(0,1644314400,[1300,5000])





