import pymongo
from scraping import url_scraper,deed_scraper
client = pymongo.MongoClient("mongodb+srv://admin:admin@cluster0.goify.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
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
    sites=url_scraper.getAllUrlsPerState(state)
    for key in sites.keys():
        if sites[key]['isTaxdeed'] == True:
            base.Taxdeeds.update_one({"siteName":key},{"$set":{str(key):sites[key]}}, upsert=True)
        if sites[key]['isTaxdeed'] == False:
            base.Foreclosures.update_one({"siteName":key},{"$set":{str(key):sites[key]}}, upsert=True)
        if sites[key]['isTaxdeed'] == None:
            base.Taxdeeds.update_one({"siteName":key},{"$set":{str(key):sites[key]}}, upsert=True)
            base.Foreclosures.update_one({"siteName":key},{"$set":{str(key):sites[key]}}, upsert=True)

def updateAuctionDB(siteObject):
    pass
    