from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from config import config


def get_driver():
    options = Options()
    options.add_argument("--headless")
    path = "chromedriver/chromedriver.exe"
    driver = webdriver.Chrome(path, options=options)
    driver.maximize_window()
    return driver

def encode_dictionary(dictionary):
    dictionary_new = dict()
    for key, value in dictionary.items():
        if type(value) == str:
            dictionary_new[key] = value.encode(config['storage_encoding'])
        elif type(value) == list:
            list_new = []
            for val in value:
                if type(val) == str:
                    list_new.append(val.encode(config['storage_encoding']))
                else:
                    list_new.append(val)
            dictionary_new[key] = list_new
        else:
            dictionary_new[key] = value
    return dictionary_new

def decode_dictionary(dictionary):
    dictionary_new = dict()
    for key, value in dictionary.items():
        if type(value) == str and is_byte_string(value):
            dictionary_new[key] = value[2:-1]
        elif type(value) == list:
            list_new = []
            for val in value:
                if type(val) == str and is_byte_string(value):
                    list_new.append(val[2:-1])
                else:
                    list_new.append(val)
            dictionary_new[key] = list_new
        else:
            dictionary_new[key] = value
    return dictionary_new

def is_byte_string(value):
    if (value[:1] == 'b'):
        if (value[1:2] == value [-1:]):
            if (value[1:2] == '\'' or value[1:2] == '\"'):
                return True
    return False

def convert_price_to_float(price):
    price = price.replace(',','')
    price = price.replace('$','')
    return float(price)
                    