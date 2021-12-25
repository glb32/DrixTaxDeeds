import requests, time, price_parser
from bs4 import BeautifulSoup
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
    url = "{}/index.cfm?zaction=AUCTION&Zmethod=UPDATE&FNC=LOAD&AREA=W&PageDir=".format(base) + str(direction) + "&doR=0&tx=" + str(nowMilliseconds()) + "&bypassPage=0"
    cookies = session.cookies.get_dict()
    result = session.get(url,cookies=cookies).text
    raw = replaceSubstrs(["@A","@B","@C","@D","@E","@F","@G","@H","@I","@J","@K","@L"],"",result)
    raw = raw.replace("\\\"","\"")
    raw = raw.strip()
    return raw

def parseDeeds(baseUrl,auctionUrl):
    
    session=requests.Session()
    session.get(auctionUrl)
    raw = getAndParseAuctionHTML(session=session,base=baseUrl,direction=0)
    
    while True:
        next_call = getAndParseAuctionHTML(session,baseUrl,1)
        if next_call in raw:
            break
        else:
            raw = raw+"\n"+next_call

    soup = BeautifulSoup(raw,features='lxml')
    cases = [element.next_sibling.text for element in soup.find_all('th',{'aria-label':'Case Number'})]
    bids = [element.next_sibling.text for element in soup.find_all(lambda tag:tag.name=="th" and "Opening Bid:" in tag.text)]
    urls = [element['href'] for element in soup.find_all('a',{'onclick':'return showExitPopup();'})]
    addresses = [str(element.next_sibling.text + ' ' + element.next.next.next.next.text) for element in soup.find_all(lambda tag:tag.name=="th" and "Property Address:" in tag.text)]
    assessed_values = [element.next_sibling.text for element in soup.find_all(lambda tag:tag.name=="th" and "Assessed Value:" in tag.text)]
    
    return (cases,bids,urls,addresses,map(price_parser.parser.parse_price,assessed_values))
