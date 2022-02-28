from ast import parse
from attr import attrs
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

def parseDeeds(auctionUrl):
    deeds = []
    session=requests.Session()
    session.get(auctionUrl)
    raw = getAndParseAuctionHTML(session=session,base=urlparse(auctionUrl).netloc,direction=0)
    
    while True:
        next_call = getAndParseAuctionHTML(session,urlparse(auctionUrl).netloc,1)
        if next_call in raw:
            break
        else:
            raw = raw+"\n"+next_call

    soup = BeautifulSoup(raw,features='lxml')
    elements = soup.find_all('div',{'aria-label':'Auction Details'})
    for element in range(len(elements)):
        
        case_no = elements[element].find('th',{'aria-label':'Case Number'}).next_sibling.text
        opening_bid = elements[element].find(lambda tag:tag.name=="th" and "Opening Bid:" in tag.text).next_sibling.text if elements[element].find(lambda tag:tag.name=="th" and "Opening Bid:" in tag.text) is not None else "ERROR:Site provided wrong data"
        parcel_url = elements[element].find(lambda tag:tag.name=="th" and "Parcel ID:" in tag.text).next_sibling.find('a',{'onclick':"return showExitPopup();"})['href'] if elements[element].find(lambda tag:tag.name=="th" and "Parcel ID:" in tag.text) is not None else elements[element].find(lambda tag:tag.name=="th" and "Alternate Key" in tag.text).next_sibling.find('a',{'onclick':"return showExitPopup();"})['href']
        parcel_address = str(elements[element].find(lambda tag:tag.name=="th" and "Property Address:" in tag.text).next_sibling.text + ' ' + elements[element].find(lambda tag:tag.name=="th" and "Property Address:" in tag.text).next.next.next.next.text) if elements[element].find(lambda tag:tag.name=="th" and "Property Address:" in tag.text) is not None else "NO ADDRESS PROVIDED, CHECK PARCEL URL"
        assessed_value = int(price_parser.parser.parse_price(elements[element].find(lambda tag:tag.name=="th" and "Assessed Value:" in tag.text).next_sibling.text).amount) if elements[element].find(lambda tag:tag.name=="th" and "Assessed Value:" in tag.text) is not None else 0

        deeds.append(Deed(case_no,opening_bid,parcel_url,parcel_address,assessed_value).__dict__)
    
    return sorted(deeds,key=lambda x: int(x['assessed_value']))
 
