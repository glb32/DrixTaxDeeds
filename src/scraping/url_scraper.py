import requests,bs4,json,re
from datetime import datetime

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
            sites[states[ID].contents[0]] =states[ID].attrs['value']
        

    for Site in sites.keys():
        sites[Site]=re.match("^.+?[^\/:](?=[?\/]|$)",json.loads(session.get(f"https://alachua.realtaxdeed.com/index.cfm?ZACTION=AJAX&ZMETHOD=LOGIN&func=SWITCH&VENDOR={sites[Site]}").content.strip())['URL']).group()
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
    auctions = {}

    for date in elem:
        if "Tax Deed" == date.next_element:
            if  datetime.strptime(date.parent.get("dayid"), '%m/%d/%Y') >= datetime.today():
                     auctions[countyName]=[{'url' : baseURL + "/index.cfm?zaction=AUCTION&Zmethod=PREVIEW&AUCTIONDATE={}".format(date.parent.get("dayid")), 'date_and_time':str(date.parent.get("dayid") + ' ' + date.find('span',{'class':'CALTIME'}).text)}]
            else:  
                if  datetime.strptime(date.parent.get("dayid"), '%m/%d/%Y') >= datetime.today():
                     auctions[countyName].append({'url': baseURL + "/index.cfm?zaction=AUCTION&Zmethod=PREVIEW&AUCTIONDATE={}".format(date.parent.get("dayid")),'date_and_time': str(date.parent.get("dayid") + ' ' + date.find('span',{'class':'CALTIME'}).text)})
    return auctions
print(getAuctionsPerCounty("https://charlotte.realforeclose.com"))