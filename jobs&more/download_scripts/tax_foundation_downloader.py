import requests

def download_file(url, filename):
    try:
        req = requests.get(url)
        filename = 'downloaded_files/' + filename + '.xlsx'
            
        with requests.get(url) as req:
            with open(filename, 'wb') as f:
                for chunk in req.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        return filename
    except Exception as e:
        print(e)
        return None
            
def update_tax_data():
    state_individual_income_tax = 'https://files.taxfoundation.org/20210217114700/State-Individual-Income-Tax-Rates-and-Brackets-for-2021.xlsx'
    fed_income_tax = 'https://files.taxfoundation.org/20210203150250/2021-Federal-Income-Tax-Rates-and-Brackets1.xlsx'
    download_file(state_individual_income_tax, 'state_tax')
    download_file(fed_income_tax, 'federal_tax')

