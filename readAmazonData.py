from lxml import html  
import csv,os,json,sys
import requests
from exceptions import ValueError
from time import sleep
 
def AmzonParser(url, asin):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
    page = requests.get(url,headers=headers)
    while True:
        sleep(3)
        try:
            doc = html.fromstring(page.content)
            XPATH_NAME = '//h1[@id="title"]//text()'
            XPATH_SALE_PRICE = '//span[contains(@id,"ourprice") or contains(@id,"saleprice")]/text()'
            XPATH_ORIGINAL_PRICE = '//td[contains(text(),"List Price") or contains(text(),"M.R.P") or contains(text(),"Price")]/following-sibling::td/text()'
            XPATH_AVAILABILITY = '//div[@id="availability"]//text()'
            XPATH_OFFER_PRICE = '//span[contains(@class,"offer-price")]//text()'
            XPATH_NUM_REVIEWS = '//span[@id="acrCustomerReviewText"]//text()'
            XPATH_RATING = '//a[@id="reviewStarsLinkedCustomerReviews"]/child::i/child::span/text()'
 
            RAW_NAME = doc.xpath(XPATH_NAME)
            RAW_SALE_PRICE = doc.xpath(XPATH_SALE_PRICE)
            RAW_ORIGINAL_PRICE = doc.xpath(XPATH_ORIGINAL_PRICE)
            RAW_AVAILABILITY = doc.xpath(XPATH_AVAILABILITY)
            RAW_OFFER_PRICE = doc.xpath(XPATH_OFFER_PRICE)
            RAW_NUM_REVIEWS = doc.xpath(XPATH_NUM_REVIEWS)
            RAW_RATING = doc.xpath(XPATH_RATING)
 
            NAME = ' '.join(''.join(RAW_NAME).split()) if RAW_NAME else ''
            SALE_PRICE = ' '.join(''.join(''.join(RAW_SALE_PRICE).replace("$", "")).split()).strip() if RAW_SALE_PRICE else ''
            ORIGINAL_PRICE = ''.join(''.join(RAW_ORIGINAL_PRICE).replace("$", "")).strip() if RAW_ORIGINAL_PRICE else ''
            AVAILABILITY = ''.join(RAW_AVAILABILITY).strip() if RAW_AVAILABILITY else ''
            OFFER_PRICE = ''.join(''.join(RAW_OFFER_PRICE[0]).replace("$", "")).strip() if RAW_OFFER_PRICE else ''
            NUM_REVIEWS = ''.join(''.join(''.join(RAW_NUM_REVIEWS).split(' ')[0]).replace(",", "")) if RAW_NUM_REVIEWS else ''
            RATING = ''.join(''.join(RAW_RATING).split(' ')[0]) if RAW_RATING else ''

            if ORIGINAL_PRICE == '':
            	if SALE_PRICE == '':
            		ORIGINAL_PRICE = OFFER_PRICE
            	else: 
                	ORIGINAL_PRICE = SALE_PRICE
 
            if page.status_code!=200:
                raise ValueError('captha')
            data = {
                    'product':NAME,
                    'salePrice':SALE_PRICE,
                    'originalPrice':ORIGINAL_PRICE,
                    'asin':asin,
                    'numReviews':NUM_REVIEWS,
                    'rating':RATING,
                    }
 
            return data
        except Exception as e:
            print e
 
def ReadAsin(ASIN):
    url = "http://www.amazon.com/dp/"+ASIN
    product_data = AmzonParser(url, ASIN)
    f=open('data.json','w')
    json.dump(product_data,f,indent=4)
 
 
if __name__ == "__main__":
    ReadAsin(sys.argv[1])