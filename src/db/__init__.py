import pymongo

client = pymongo.MongoClient("mongodb+srv://admin:admin@cluster0.goify.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = client.DrixTaxDeeds
collection = db.sites

class Site:
    def __init__(self,siteURL,siteName):
        self.siteURL = siteURL
        self.siteName = siteName
    
def insertIntoDB(object):
    collection.insert_one(object)
