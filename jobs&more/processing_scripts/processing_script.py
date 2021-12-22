import pandas as pd
from utils.util_service import decode_dictionary
import regex as re
from config import config

def get_average_rent(city='new-york-ny', num_of_beds=2):
    my_new_place_data = pd.read_csv('downloaded_data/mynewhome_data')
    results_df = my_new_place_data[(my_new_place_data['City'] == str(city.encode(config['storage_encoding']))) 
                                  & (my_new_place_data['NumOfBed'] == num_of_beds)
                                  & (my_new_place_data['Price'] > 0)]
    return results_df['Price'].mean()

def get_rental_options(city, num_of_beds):
    my_new_place_data = pd.read_csv('downloaded_data/mynewhome_data')
    results_df = my_new_place_data[(my_new_place_data['City'] == str(city.encode(config['storage_encoding']))) 
                                  & (my_new_place_data['NumOfBed'] == num_of_beds)]
    rental_options = []
    for index, row in results_df.iterrows():
        option = decode_dictionary(row)
        rental_options.append(option)
    return rental_options


def get_total_salary(married = False, num_of_beds = 1):
    job_data = pd.read_csv('downloaded_data/career_builder_data')
    state_url = pd.read_csv('predefined_data/state_url_mapping.csv')
    state_tax = pd.read_csv('predefined_data/state_tax_mapping.csv')
    fed_tax = pd.read_excel("downloaded_files/federal_tax.xlsx",sheet_name='Table 1',header = 1)
    tax = pd.read_excel("downloaded_files/state_tax.xlsx",sheet_name='2021',header =[0, 1])
    tax.loc[tax[('Unnamed: 0_level_0','State')].str.startswith('(').fillna(False), ('Unnamed: 0_level_0','State')] = None
    tax[('Unnamed: 0_level_0','State')] = tax[('Unnamed: 0_level_0','State')].fillna(method='ffill')
    tax = tax.fillna(0)
    job_data['Fed_Tax'] = 0.0
    job_data['state_tax'] = 0.0
    job_data.drop('summary', axis = 1, inplace = True)
    for i in range(0,len(job_data)):
        job_data.at[i, 'title'] = str(job_data.loc[i]['title'])[2:-1]
        job_data.at[i, 'company'] = str(job_data.loc[i]['company'])[2:-1]
        job_data.at[i, 'location'] = str(job_data.loc[i]['location'])[2:-1]
        job_data.at[i, 'url'] = str(job_data.loc[i]['url'])[2:-1]
    if not married:
        for i in range(0,len(job_data)):
            for j in range(0,len(fed_tax)):
                x = float(re.sub('[^A-Za-z0-9]+', '', fed_tax['For Unmarried Individuals'][j].split("to")[0].strip()))
                y = float(re.sub('[^A-Za-z0-9]+', '', fed_tax['For Unmarried Individuals'][j].split("to")[1].strip()))
                if job_data['salary'][i]>=x and job_data['salary'][i]<y:
                    job_data['Fed_Tax'][i]= fed_tax['Rate'][j]
                    break
    else:
         for i in range(0,len(job_data)):
            for j in range(0,len(state_tax)):
                x = float(re.sub('[^A-Za-z0-9]+', '', fed_tax['For Married Individuals Filing Joint Returns'][j].split("to")[0].strip()))
                y = float(re.sub('[^A-Za-z0-9]+', '', fed_tax['For Married Individuals Filing Joint Returns'][j].split("to")[1].strip()))
                if job_data['salary'][i]>=x and job_data['salary'][i]<=y:
                    job_data['Fed_Tax'][i]= fed_tax['Rate'][j]
                    break



    job_data['state_abb'] = job_data['location']
    job_data = job_data.loc[job_data['salary'] > 0]
    job_data = job_data.reset_index(drop=True)
    for i in range(0,len(job_data)):
        for j in range(0,len(state_url)):
            if(job_data['location'][i].__contains__(state_url['careerbuilder'][j])):
                for k in range(0,len(state_tax)):
                    if(state_tax['Abbreviation'][k]== state_url['State'][j]):
                        job_data['state_abb'][i] = state_tax['Tax Form'][k]

    if not married:
        for i in range(0,len(job_data)):
            for j in range(0,len(tax)):
                if(tax[('Unnamed: 0_level_0','State')][j]).__contains__(job_data['state_abb'][i]):
                    if (job_data['salary'][i] > tax[('Single Filer','Brackets')][j] and job_data['salary'][i] < tax[('Single Filer','Brackets')][j+1]):
                        job_data['state_tax'][i] = tax[('Single Filer','Rates')][j]
        for i in range(0,len(job_data)):
            if job_data['state_abb'][i] == 'Ill.':
                job_data['state_tax'][i] =0.0495
            elif job_data['state_abb'][i]=='Mass.':
                job_data['state_tax'][i] =0.05   
            elif job_data['state_abb'][i]=='Tex.':
                job_data['state_tax'][i] =0
            elif job_data['state_abb'][i] == 'Ariz.':
                job_data['state_tax'][i] = 0.0259
            elif job_data['state_abb'][i] == 'Ind.':
                job_data['state_tax'][i] = 0.0259

    job_data['total_tax'] = 0.0

    for i in range(0,len(job_data)):
        job_data['total_tax'][i] = job_data['salary'][i]*(job_data['state_tax'][i]+job_data['Fed_Tax'][i])
    
    pd.set_option("display.max_rows", None, "display.max_columns", None)
    
    job_data['average_rent'] = 0.0
    cities = pd.read_csv('predefined_data/state_url_mapping.csv')
    for i in range(0, len(job_data)):
        for j in range(0, len(cities)):
            if job_data['location'][i] == cities['dice'][j]:
                job_data['average_rent'][i] = get_average_rent(cities['mynewhome'][j], num_of_beds)
            
    job_data['effective_salary'] = 0.0
    for i in range(0, len(job_data)):
        job_data['effective_salary'] = job_data['salary'] - job_data['total_tax'] - job_data['average_rent']*12

    
    print(job_data.head(20))
    
def get_company_news():
    news = pd.read_csv('downloaded_data/cnbc_data')
    print(news)

