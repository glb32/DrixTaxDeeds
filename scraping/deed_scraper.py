import requests, time, price_parser,calendar
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from urllib.parse import parse_qs
from dateutil import parser

class Deed():
    def __init__(self, case_no, opening_bid, url, property_address, assessed_value,timestamp=None):
        self.case_no = case_no
        self.opening_bid = opening_bid
        self.url = url
        self.property_address = property_address
        self.assessed_value = assessed_value
        self.timestamp = timestamp
        
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


    parsed = urlparse(auctionUrl)
    captured_value = parse_qs(parsed.query)['AUCTIONDATE'][0]
    
    while True:
        next_call = getAndParseAuctionHTML(session,urlparse(auctionUrl).netloc,1)
        if next_call in raw:
            break
        else:
            raw = raw+"\n"+next_call

    soup = BeautifulSoup(raw,features='lxml')
    for element in soup.find_all('div',{'aria-label':'Auction Details'}):
        case_no = element.find('th',{'aria-label':'Case Number'}).next_sibling.text
        opening_bid = element.find(lambda tag:tag.name=="th" and "Opening Bid:" in tag.text).next_sibling.text if element.find(lambda tag:tag.name=="th" and "Opening Bid:" in tag.text) is not None else "ERROR:Site provided wrong data"
        parcel_url = element.find_all('a',{'onclick':'return showExitPopup();'})[1].attrs['href'] if len(element.find_all('a',{'onclick':'return showExitPopup();'})) >1 else element.find_all('a',{'onclick':'return showExitPopup();'})[0].attrs['href']
        parcel_address = str(element.find(lambda tag:tag.name=="th" and "Property Address:" in tag.text).next_sibling.text + ' ' + element.find(lambda tag:tag.name=="th" and "Property Address:" in tag.text).next.next.next.next.text) if element.find(lambda tag:tag.name=="th" and "Property Address:" in tag.text) is not None else "NO ADDRESS PROVIDED, CHECK PARCEL URL"
        assessed_value = int(price_parser.parser.parse_price(element.find(lambda tag:tag.name=="th" and "Assessed Value:" in tag.text).next_sibling.text).amount) if element.find(lambda tag:tag.name=="th" and "Assessed Value:" in tag.text) is not None else 0
        
        deeds.append(Deed(case_no,opening_bid,parcel_url,parcel_address,assessed_value,timestamp=calendar.timegm(parser.parse(captured_value).timetuple())).__dict__)
    
    return sorted(deeds,key=lambda x: int(x['assessed_value']))
   
