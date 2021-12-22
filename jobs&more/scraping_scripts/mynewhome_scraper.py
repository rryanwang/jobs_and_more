from utils.util_service import get_driver, encode_dictionary, convert_price_to_float
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
from urllib.request import urlopen
from bs4 import BeautifulSoup
from selenium.webdriver.common.action_chains import ActionChains
import csv
import pandas as pd

def refresh_homes():
    urls_list = []
    house_options = []
    urlPrefix = 'https://www.mynewplace.com'
    apartmentPrefix = '/apartments-for-rent/'
    cities = pd.read_csv('predefined_data/state_url_mapping.csv')['mynewhome']
    for city in cities:
        driver = get_driver()
        driver.get(urlPrefix)
        wait = WebDriverWait(driver, 3)
        arrow = wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'arrow')]")))
        arrow.click()
        time.sleep(3)
        element = driver.find_element_by_class_name('clearfix')
        driver.execute_script("""
        var element = arguments[0];
        element.parentNode.removeChild(element);
        """, element)
        cityLink = driver.find_element_by_xpath("*//a[contains(@href, '" + str(apartmentPrefix + city) + "')]")
        ActionChains(driver).move_to_element(cityLink).perform()
        time.sleep(2)
        cityLink.click()
        time.sleep(3)
        for i in range(1, 4):
            filter = wait.until(EC.visibility_of_element_located((By.XPATH, "//a[contains(@onclick, 'toggleFilter()')]")))
            filter.click()
            select = wait.until(EC.visibility_of_element_located((By.XPATH, "//select[contains(@id, 'beds')]")))
            select.click()
            option = wait.until(EC.visibility_of_element_located((By.XPATH, "//option[contains(@value, "+ str(i) +")]")))
            option.click()
            time.sleep(2)
            update = wait.until(EC.visibility_of_element_located((By.XPATH, "//button[contains(@type, 'submit')]")))
            update.click()
            time.sleep(3)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            try:
                urlList = soup.findAll('div',{ "id" : "listings"} )[0]
                addUrl = "https://www.mynewplace.com"
                for i in urlList:
                    resultDict = {}
                    resultDict['url'] = addUrl+i.get("href")
                    resultDict['city'] = city
                    urls_list.append(resultDict)
            except:
                continue
        driver.quit()
    for element in urls_list:
        house_options.extend(url2Dic(element['url'], element['city']))
    csv_columns = ['Price', 'Address', 'NumOfBed', 'Amenities', 'City', 'Url']
    with open('downloaded_data/mynewhome_data', 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for data in house_options:
            price = data['Price']
            # if price not mentioned, put it as 0
            if price == 'Please Call':
                data['Price'] = 0
            elif type(price) == str:
                data['Price'] = convert_price_to_float(price)
            writer.writerow(encode_dictionary(data))
        csvfile.truncate()   
        

"""
getUrl method will take the Url for one single city as the parameter, and return
a list of url which refers to all the houses page in that city.
"""

"""
url2Dic method will take the Url for one single house as the parameter, and return
a dictionary of the house information, including Price, Address, Amenities 
"""
    
def url2Dic(url, city):
    info_list = ['Price', 'Address','NumOfBed','Amenities']
    
    option1_info = {'City': city, 'Url': url}
    option2_info = {'City': city, 'Url': url}
    option_info = {'City': city, 'Url': url}
    for i in info_list:
        option1_info[i] = []
        option2_info[i] = []
        option_info[i] = []
    
        
    html = urlopen(url)
    bsyc1 = BeautifulSoup(html.read(), "lxml")
    
    """Find the address"""
    addressWithTag =bsyc1.findAll('h5',{"class":"property-address"})[0]
    address = addressWithTag.text
    
    """Find the price or maxPrice & minPrice"""
    priceWithTag= bsyc1.findAll('h1',{ "class" : "price-range"} )[0]
    price = priceWithTag.text

    maxPrice = ''
    minPrice = ''
    if '-' in price:
        price_range = price.split('-')
        minPrice = convert_price_to_float(price_range[0].strip())
        maxPrice = convert_price_to_float(price_range[1].strip())

    """Find the number of Bedroom, or a range of number for bedroom"""
    bed_bath_Tag = bsyc1.findAll('h5',{"class":"bed-bath"})[0]

    bed_bath_str = bed_bath_Tag.text
    if ('Bed' not in bed_bath_str):
        return []
    bed_bath = bed_bath_str.split('Bed')

    noOfBed = 0
    maxBed = 0
    minBed = 0
    bed_range = bed_bath[0]

    if '-' in bed_range:
        bed_option_str = bed_bath[0].split('-')
        bed_option = []
        for i in bed_option_str:
            bed_option.append(int(i.strip()))

        if bed_option[0] == bed_option[1]:
            noOfBed = bed_option[0]
            maxBed = noOfBed
            minBed = noOfBed
        else:
            minBed = bed_option[0]
            maxBed = bed_option[1]
            noOfBed = maxBed
    else:
        noOfBed = int(bed_bath[0].strip())
        maxBed = noOfBed
        minBed = noOfBed
    
        
        
    """Find the list of Amenities"""
    amenWithTag = bsyc1.findAll('ul', {"class": "amenities-list"})
    
    amenList = []
    if len(amenWithTag) > 0:
        for i in  amenWithTag[0]:
            temp = i.text
            amenList.append(temp)
        

    """Create a list of dictionary and stores all the possible outcome"""

    house_options = []
    
    if '-' not in price and '-' not in bed_range:
        option1_info['Price']  = price
        option1_info['Address'] = address
        option1_info['NumOfBed'] = noOfBed
        option1_info['Amenities'] = amenList
        house_options.append(option1_info)
    
    elif '-' in price and '-' not in bed_range:
        avg_price = (int(maxPrice)+int(minPrice))/2
        option1_info['Price']  = avg_price
        option1_info['Address'] = address
        option1_info['NumOfBed'] = minBed
        option1_info['Amenities'] = amenList
        house_options.append(option1_info)


    elif '-' not in price and '-' in bed_range :
        option1_info['Price']  = price
        option1_info['Address'] = address
        option1_info['NumOfBed'] = noOfBed
        option1_info['Amenities'] = amenList
        house_options.append(option1_info)
        


    elif '-' in price and '-'in bed_range:
        if minPrice == maxPrice and minBed == maxBed:
            option1_info['Price']  = maxPrice
            option1_info['Address'] = address
            option1_info['NumOfBed'] = maxBed
            option1_info['Amenities'] = amenList
            house_options.append(option1_info)
        
        if minPrice != maxPrice and minBed == maxBed:
            option1_info['Price']  = maxPrice
            option1_info['Address'] = address
            option1_info['NumOfBed'] = maxBed
            option1_info['Amenities'] = amenList
            house_options.append(option1_info)


        elif minPrice != maxPrice and minBed != maxBed:
            int_maxPrice = int(maxPrice)
            int_minPrice = int(minPrice)
            price_range = int_maxPrice - int_minPrice
            bed_range = maxBed - minBed
            gap = price_range / bed_range
            i = minBed
            currentPrice = int_minPrice
            for k in range(minBed, maxBed+1):
                option_info = {'City': city, 'Url': url}
                for i in info_list:
                    option_info[i] = []
                option_info['Price']  = currentPrice
  
                currentPrice += gap

                option_info['Address'] = address
                option_info['NumOfBed'] = k
                option_info['Amenities'] = amenList
                house_options.append(option_info)

    """
    for each dictionary in the list of 'house_otions',the data type is
                'Price':         String
                'Address':       String
                'NumOfBed':      int
                'Amenities':     list
                'City':          String
                'Url':           String
"""
    return house_options