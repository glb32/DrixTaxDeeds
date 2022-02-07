from ast import Suite
from email.mime import base
import requests,bs4,json,re
from datetime import datetime
from dateutil import parser
import pytz,calendar
class Auction:
    def __init__(self,date,location,url,deeds,unixTimestamp):
        self.date=date
        self.unixTimestamp = unixTimestamp
        self.location=location
        self.url=url
        self.deeds=deeds
class Site:
    def __init__(self,name,url,isTaxdeed=None):
        self.name = name
        self.url =url
        self.isTaxdeed = isTaxdeed

'''
getAllUrlsPerState(state)
@param
state:int(0,3)

@desc:
fetches all URLs for a state(AZ,CO,FL,NJ)
'''
def getAllUrlsPerState(state):
    session = requests.Session()
    soup = bs4.BeautifulSoup(session.get('https://alachua.realtaxdeed.com').content,features='lxml')
    states=soup.find_all('optgroup')[state].contents
    sites={}
    site = []
    for ID in range(len(states)):
        if ID % 2 != 0:
            sites[re.sub('\.','',states[ID].contents[0])] =states[ID].attrs['value']
    

    for SiteName in sites.keys():
        if "Taxdeed" in SiteName or "Tax Deed" in SiteName:
            site.append(Site(SiteName,re.match("^.+?[^\/:](?=[?\/]|$)",json.loads(session.get(f"https://alachua.realtaxdeed.com/index.cfm?ZACTION=AJAX&ZMETHOD=LOGIN&func=SWITCH&VENDOR={sites[SiteName]}").content.strip())['URL']).group(),isTaxdeed=True).__dict__)
           
        elif "Foreclosure" in SiteName:
             site.append(Site(SiteName,re.match("^.+?[^\/:](?=[?\/]|$)",json.loads(session.get(f"https://alachua.realtaxdeed.com/index.cfm?ZACTION=AJAX&ZMETHOD=LOGIN&func=SWITCH&VENDOR={sites[SiteName]}").content.strip())['URL']).group(),isTaxdeed=False).__dict__)
        elif "." in SiteName or "-" in SiteName:
             site.append(Site(re.sub("\.-","",SiteName),re.match("^.+?[^\/:](?=[?\/]|$)",json.loads(session.get(f"https://alachua.realtaxdeed.com/index.cfm?ZACTION=AJAX&ZMETHOD=LOGIN&func=SWITCH&VENDOR={sites[SiteName]}").content.strip())['URL']).group(),isTaxdeed=None).__dict__)
            
        else:
            site.append(Site(SiteName,re.match("^.+?[^\/:](?=[?\/]|$)",json.loads(session.get(f"https://alachua.realtaxdeed.com/index.cfm?ZACTION=AJAX&ZMETHOD=LOGIN&func=SWITCH&VENDOR={sites[SiteName]}").content.strip())['URL']).group(),isTaxdeed=None).__dict__)
    
    site.append(Site('Alachua Taxdeed',"https://alachua.realtaxdeed.com",True).__dict__)
    return site

'''
getAuctionsPerCounty(county)
@param
county:str

@desc:
gets all auctions for a county (e.g. Clay, Duval, etc.)
'''
def getAuctionsPerCounty(baseURLs):
    auctions = []
    for baseURL in baseURLs:

        soup = bs4.BeautifulSoup(requests.get(baseURL['url']+ "/index.cfm?zaction=USER&zmethod=CALENDAR").content,'lxml')   
        elem = soup.find_all("span", {"class": "CALTEXT"})
        countyName = baseURL['name']

       
        for date in elem:
            if "Tax Deed" == date.next_element:
                if  parser.parse(date.parent.get("dayid")+date.parent.find("span",{"class":"CALTIME"}).text,tzinfos={"CT":-6*3600,"ET":-5*3600}) >= datetime.now(pytz.timezone("US/Eastern")):
                        auctions.append(Auction(url= baseURL['url'] + "/index.cfm?zaction=AUCTION&Zmethod=PREVIEW&AUCTIONDATE={}".format(date.parent.get("dayid")), date =str(date.parent.get("dayid") + ' ' + date.find('span',{'class':'CALTIME'}).text),location=countyName,deeds=[],unixTimestamp=calendar.timegm(parser.parse(date.parent.get("dayid")+date.parent.find("span",{"class":"CALTIME"}).text, tzinfos = {"CT":-6*3600,"ET":-5*3600}).timetuple())).__dict__)
                else:  
                    continue
        

    return auctions



