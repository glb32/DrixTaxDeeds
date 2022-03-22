import requests, time, price_parser,re
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
def replaceSubstrs(string):
    string = string.replace("@A",'<div class="')
    string = string.replace("@B",'</div>')
    string = string.replace("@C",'class="')
    string = string.replace("@D",'<div>')
    string = string.replace("@E",'AUCTION')
    string = string.replace("@F",'</td><td')
    string = string.replace("@G",'</td></tr>')
    string = string.replace("@H",'<tr><td ')
    string = string.replace("@I",'table')
    string = string.replace("@J",'p_back="NextCheck=')
    string = string.replace("@K",'style="Display:none"')
    string = string.replace("@L",'/index.cfm?zaction=auction&zmethod=details&AID=')
    return string

def getAndParseAuctionHTML(session,base,direction):
    #get data
    url = "https://{}/index.cfm?zaction=AUCTION&Zmethod=UPDATE&FNC=LOAD&AREA=W&PageDir=".format(base) + str(direction) + "&doR=0&tx=" + str(nowMilliseconds()) + "&bypassPage=0"
    cookies = session.cookies.get_dict()
    result = session.get(url,cookies=cookies).text
    raw = replaceSubstrs(result)
    raw = raw.replace("\\\"","\"")
    raw = raw.strip()
    return raw

def parseDeeds(auction):
    deeds = []
    divs =[]
    aid=None
    ids = None
    session=requests.Session()
    session.get(auction['url'])
    raw = [getAndParseAuctionHTML(session=session,base=urlparse(auction['url']).netloc,direction=0)]
    
    while True:
        next_call = getAndParseAuctionHTML(session,urlparse(auction['url']).netloc,1)
        if next_call in raw:
            break
        else:
            raw.append(next_call)
    
    for document in raw:
        aid = document.split("rlist")[1]
        ids=re.findall('\d{7}',aid)
        soup = BeautifulSoup(document)
        for id in ids:
            div = soup.find('div',{'aid':id})
            divs.append(div)
        for div in divs:
            case_no = div.find('th',{'aria-label':'Case Number'}).next_sibling.text
            opening_bid = div.find(lambda tag:tag.name=="th" and "Opening Bid:" in tag.text).next_sibling.text if div.find(lambda tag:tag.name=="th" and "Opening Bid:" in tag.text) is not None else "ERROR:Site provided wrong data"
            parcel_url = div.find(lambda tag:tag.name=="th" and "Parcel ID:" in tag.text).next_sibling.find('a',{'onclick':"return showExitPopup();"})['href'] if div.find(lambda tag:tag.name=="th" and "Parcel ID:" in tag.text) is not None else div.find(lambda tag:tag.name=="th" and "Alternate Key" in tag.text).next_sibling.find('a',{'onclick':"return showExitPopup();"})['href']
            parcel_address = str(div.find(lambda tag:tag.name=="th" and "Property Address:" in tag.text).next_sibling.text + ' ' + div.find(lambda tag:tag.name=="th" and "Property Address:" in tag.text).next.next.next.next.text) if div.find(lambda tag:tag.name=="th" and "Property Address:" in tag.text) is not None else "NO ADDRESS PROVIDED, CHECK PARCEL URL"
            assessed_value = int(price_parser.parser.parse_price(div.find(lambda tag:tag.name=="th" and "Assessed Value:" in tag.text).next_sibling.text).amount) if div.find(lambda tag:tag.name=="th" and "Assessed Value:" in tag.text) is not None else 0

            deeds.append(Deed(case_no,opening_bid,parcel_url,parcel_address,assessed_value).__dict__)
        divs.clear()
        
    auction['deeds']=sorted(deeds,key=lambda x: int(x['assessed_value']))
    return auction
parseDeeds({'url':'https://lee.realtaxdeed.com/index.cfm?zaction=AUCTION&Zmethod=PREVIEW&AUCTIONDATE=03/29/2022','deeds':[]})