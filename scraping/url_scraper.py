import requests,bs4,json,re
from datetime import datetime

class Auction:
    def __init__(self,date,location,url,deeds):
        self.date=date
        self.location=location
        self.url=url
        self.deeds=deeds

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
    for ID in range(len(states)):
        if ID % 2 != 0:
            sites[re.sub('\.','',states[ID].contents[0])] =states[ID].attrs['value']
    

    for Site in sites.keys():
        if "Taxdeed" in Site or "Tax Deed" in Site:
           sites[Site] ={'isTaxdeed':True , 'siteUrl':re.match("^.+?[^\/:](?=[?\/]|$)",json.loads(session.get(f"https://alachua.realtaxdeed.com/index.cfm?ZACTION=AJAX&ZMETHOD=LOGIN&func=SWITCH&VENDOR={sites[Site]}").content.strip())['URL']).group()}
        elif "Foreclosure" in Site:
             sites[Site] ={'isTaxdeed':False , 'siteUrl':re.match("^.+?[^\/:](?=[?\/]|$)",json.loads(session.get(f"https://alachua.realtaxdeed.com/index.cfm?ZACTION=AJAX&ZMETHOD=LOGIN&func=SWITCH&VENDOR={sites[Site]}").content.strip())['URL']).group()}
        else:
            sites[Site] ={'isTaxdeed':None , 'siteUrl':re.match("^.+?[^\/:](?=[?\/]|$)",json.loads(session.get(f"https://alachua.realtaxdeed.com/index.cfm?ZACTION=AJAX&ZMETHOD=LOGIN&func=SWITCH&VENDOR={sites[Site]}").content.strip())['URL']).group()}
    sites['Alachua Taxdeed'] ={'isTaxdeed':True , 'siteUrl':"https://alachua.realtaxdeed.com"}
    return sites

'''
getAuctionsPerCounty(county)
@param
county:str

@desc:
gets all auctions for a county (e.g. Clay, Duval, etc.)
'''
def getAuctionsPerCounty(baseURL):
    soup = bs4.BeautifulSoup(requests.get(baseURL + "/index.cfm?zaction=USER&zmethod=CALENDAR").content,'lxml')   
    elem = soup.find_all("span", {"class": "CALTEXT"})
    countyName = re.findall("(?<=\/\/)(.*?)(?=\.)",baseURL)[0]
    auctions = []

    for date in elem:
        if "Tax Deed" == date.next_element:
            if  datetime.strptime(date.parent.get("dayid"), '%m/%d/%Y') >= datetime.today():
                     auctions.append(Auction(url= baseURL + "/index.cfm?zaction=AUCTION&Zmethod=PREVIEW&AUCTIONDATE={}".format(date.parent.get("dayid")), date =str(date.parent.get("dayid") + ' ' + date.find('span',{'class':'CALTIME'}).text),location=countyName,deeds=[]))
            else:  
                continue
    return auctions



