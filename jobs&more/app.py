from apis.cnbc_api import get_news_data
from download_scripts.tax_foundation_downloader import update_tax_data
from scraping_scripts.careerbuilder_scraper import refresh_salaries
from scraping_scripts.dice_scraper import refresh_jobs
from scraping_scripts.mynewhome_scraper import refresh_homes
from processing_scripts.processing_script import get_rental_options, get_company_news, get_total_salary
import pandas as pd
1
input_prompt = '''
1 - Show top 20 new jobs
2 - Show top company news
3 - Show rental apartments
4 - Refresh data
'''

refresh_confirmation_prompt = '''
This refresh takes more than 3 hours on a good day.
Are you sure you wanna go ahead? (y/n)
'''

starting_prompt = '''
Welcome to Jobs And More
To serve you better, we need some information from you!
Funny question to start with, but are you married?(y/n)
'''

second_prompt = '''
Thanks for that, your data will be safe with us, prmomise!
Next, can you tell us how many rooms do you require in your house?(1/2/3)
'''


def refresh_stats():
    print('Scraping jobs from dice.com ...')
    #refresh_jobs()
    print('Scraping salaries from careerbuilder.com ...')
    #refresh_salaries()
    print('Scraping house rentals from mynewhome.com ...')
    #refresh_homes()
    print('Downloading tax data from taxfoundation.com ...')
    #update_tax_data()
    print('Fetching financial news from cnbc api ...')
    #get_news_data()
    print('All data successfully updated!')
    
def show_rental_apartments(beds):
    cities = pd.read_csv('predefined_data/state_url_mapping.csv')
    print("Enter the index for the city you want:")
    for index, row in cities.iterrows():
        print(index, row['City'])
    val = int(input())
    city = None
    cityName = None
    for index, row in cities.iterrows():
        if val == index:
            city = row['mynewhome']
            cityName = row['City']
    print(str(beds) + " bed apartments in " + cityName + ":")
    for item in get_rental_options(city, beds):
        print(item['Address'] + " (" + item['Url'] + ')')
        print("Cost = $" + str(item['Price']))
    

if __name__ == '__main__':
    status = input(starting_prompt)
    if status == 'y':
        married = True
    else:
        married = False
    beds = int(input(second_prompt))
    while True:
        val = input(input_prompt)
        if val == '1':
            get_total_salary()
        elif val == '2':
            get_company_news()
        elif val == '3':
            show_rental_apartments(beds)
        elif val == '4':
            val1 = input(refresh_confirmation_prompt)
            if val1 == 'y':
                refresh_stats()
        else:
            break
