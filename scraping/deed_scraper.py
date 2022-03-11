from ast import parse
import requests, time, price_parser
from bs4 import BeautifulSoup
from urllib.parse import urlparse


class Deed():
    def __init__(self, case_no, opening_bid, url, property_address, assessed_value):
        self.case_no = case_no
        self.opening_bid = opening_bid
        self.url = url
        self.property_address = property_address
        self.assessed_value = assessed_value
        
#current time in milliseconds
def nowMilliseconds():
   return int(time.time() * 1000)

#replace substrings in bytes result
def replaceSubstrs(substring_list,replace,string):
    for subs in substring_list:
        string = string.replace(subs,replace)
    return string

def getAndParseAuctionHTML(session,base,direction):
    #get data
    url = "https://{}/index.cfm?zaction=AUCTION&Zmethod=UPDATE&FNC=LOAD&AREA=W&PageDir=".format(base) + str(direction) + "&doR=0&tx=" + str(nowMilliseconds()) + "&bypassPage=0"
    cookies = session.cookies.get_dict()
    result = session.get(url,cookies=cookies).text
    raw = replaceSubstrs(["@A","@B","@C","@D","@E","@F","@G","@H","@I","@J","@K","@L"],"",result)
    raw = raw.replace("\\\"","\"")
    raw = raw.strip()
    return raw

def parseDeeds(auction):
    deeds = []
    session=requests.Session()
    session.get(auction['url'])
    raw = getAndParseAuctionHTML(session=session,base=urlparse(auction['url']).netloc,direction=0)
    
    while True:
        next_call = getAndParseAuctionHTML(session,urlparse(auction['url']).netloc,1)
        if next_call in raw:
            break
        else:
            raw = raw+"\n"+next_call

    soup = BeautifulSoup(raw,features='lxml')
    with open('raw.html','w+')as html:
        html.write(raw)
        html.close()
    elements = soup.find_all('div',{'class':'AUCTION_DETAILS'})
    for element in range(len(elements)):
        data = elements[element].find_all('td')
        case_no=data[1]
        opening_bid = data[2]
        parcel_url = data[3].next_sibling.attrs['href']
        parcel_address = str(data[4].text + data[5].text if data[5] is not None else '')
        #assessed_value = int( price_parser.parser.parse_price(data[6] if data[6] is not None and data else 0) )
       
        deeds.append(Deed(case_no,opening_bid,parcel_url,parcel_address,assessed_value).__dict__)
    
    auction['deeds']=sorted(deeds,key=lambda x: int(x['assessed_value']))
    return auction
a={'url':'https://hillsborough.realtaxdeed.com/index.cfm?zaction=AUCTION&Zmethod=PREVIEW&AUCTIONDATE=03/24/2022','deeds':[]}
parseDeeds(a)