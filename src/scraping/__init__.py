import url_scraper,deed_scraper


class Auction:
    def __init__(self,date,url,deeds):
        self.date=date
        self.url=url
        self.deeds=deeds

class Deed():
    def __init__(self, case_no, opening_bid, url, property_address, assessed_value,location):
        self.case_no = case_no
        self.opening_bid = opening_bid
        self.url = url
        self.property_address = property_address
        self.assessed_value = assessed_value
        self.location= location
        
