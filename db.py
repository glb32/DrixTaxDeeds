import pymongo
from scraping import url_scraper,deed_scraper
from itertools import chain
import concurrent.futures
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
    data = []
    auction_processes = []
    auctions=[]
    output =[]
    for dataEntry in base.Taxdeeds.find({}):
        data.append(dataEntry)

    with concurrent.futures.ThreadPoolExecutor() as Executor:
        for site in range(len(data)):
            auction_processes.append(Executor.submit(url_scraper.getAuctionsPerCounty,data[site]))
        
    auctions = list(chain.from_iterable([auction._result for auction in auction_processes]))

    with concurrent.futures.ThreadPoolExecutor() as Executor:
        for auction in auctions:
            output.append(Executor.submit(deed_scraper.parseDeeds,auction))
    parsed = [auction._result for auction in output]
    
    client.DrixTaxDeeds.Auctions.delete_many({})
    client.DrixTaxDeeds.Auctions.insert_many(parsed)
    return 0


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
def fetchDeedsInDesiredRangeAndCounty(date1,date2,county,price=None):
    auctions=client.DrixTaxDeeds.Auctions.find({"$and":[{"unixTimestamp":{"$gte":date1,"$lte":date2}},{"location":county}]})
    arr=[]
    for auction in auctions:
        arr.append(extractDeeds(auction))
    if price is None:
        pass
    else:
        for auction in range(len(arr)):
            arr[auction]=[deed for deed in arr[auction] if deed['assessed_value']>=price[0] and deed['assessed_value']<=price[1]]
        
    return arr
def fetchAllAuctions():
    deeds = client.DrixTaxDeeds.Auctions.find({})
    return deeds

def fetchDeedsByCounty(county):
    auctions = client.DrixTaxDeeds.Auctions.find({"location":county})
    arr = []
    for auction in auctions:
        arr.append(auction['deeds'])
    return arr

def fetchNearestAuctions(date1,date2):
    auctions = client.DrixTaxDeeds.Auctions.find({"unixTimestamp":{"$gte":date1,"$lte":date2}})
    return auctions
def RemoveAuction(auction):
    client.DrixTaxDeeds.Auctions.delete_one({'_id':auction['_id']})

if __name__ =="__main__":
    updateAuctionDB()