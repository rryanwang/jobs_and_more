from bs4 import BeautifulSoup
from utils.util_service import get_driver, encode_dictionary, decode_dictionary, convert_price_to_float
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import pandas as pd
import csv

def refresh_salaries():
    dice_data = pd.read_csv('downloaded_data/dice_data', encoding='ascii')
    city_mapping = pd.read_csv('predefined_data/state_url_mapping.csv')
    companies = []
    salaries = []
    for index, row in dice_data.iterrows():
        company_dict = {}
        company_dict = {'title':row['title'], 'company':row['company'], 'location': row['location'],
               'url':row['url'], 'summary':row['summary']}
        for index1, row1 in city_mapping.iterrows():
            if company_dict['location'] == row1['dice']:
                company_dict['location'] = row1['careerbuilder']
                break
        dic = decode_dictionary(company_dict)
        companies.append(dic)
    for company in companies:
        driver = get_driver()
        driver.get('https://www.careerbuilder.com/salary')
        # handling reandom time out exceptions
        try:
            wait = WebDriverWait(driver, 3)
            keyword = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[contains(@id, 'keywords')]")))
            keyword.clear()
            keyword.send_keys(company['company'] + " " + company['title'])
            loc = driver.find_element_by_id('location-searched')
            loc.clear()
            loc.send_keys(company['location'])
            submit = wait.until(EC.visibility_of_element_located((By.XPATH, "//button[contains(@id, 'sbmt')]")))
            submit.click()
            time.sleep(3)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            sal = soup.findAll('div', { "class" : "fl-l"} )
            salary = sal[0].text
        except:
            continue;
        company_with_salary = company
        company_with_salary['salary'] = convert_price_to_float(salary)
        salaries.append(company_with_salary)
        driver.quit()
    csv_columns = ['title', 'company', 'location', 'url', 'summary', 'salary']
    with open('downloaded_data/career_builder_data', 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for data in salaries:
            writer.writerow(encode_dictionary(data))
        csvfile.truncate()