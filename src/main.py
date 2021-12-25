import pymongo
import db, scraping

def buildDB():
    sites=scraping.getAllUrlsPerState(2)
    for key in sites.keys():
        db.insertIntoDB({key:sites[key]})
buildDB()