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

def fetchDeedsInDesiredRange(date1,date2,price=None):
    auctions=client.DrixTaxDeeds.Auctions.find({"unixTimestamp":{"$gte":date1,"$lte":date2}})
    arr=[]
    for auction in auctions:
        arr.append(extractDeeds(auction))
    if price is None:
        pass
    else:
        for auction in range(len(arr)):
            arr[auction]=[deed for deed in arr[auction] if deed['assessed_value']>=price[0] and deed['assessed_value']<=price[1]]
        
    return arr

def fetchDeedsByCounty(county):
    auctions = client.DrixTaxDeeds.Auctions.find({"location":county})
    arr = []
    for auction in auctions:
        arr.append(auction['deeds'])
    return arr

def fetchNearestAuctions(date1,date2):
    auctions = client.DrixTaxDeeds.Auctions.find({"unixTimestamp":{"$gte":date1,"$lte":date2}})
    return auctions