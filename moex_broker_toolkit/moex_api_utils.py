import requests

def get_last_price(ticker):
    url = f"https://iss.moex.com/iss/engines/stock/markets/shares/securities/{ticker}.json?iss.only=marketdata"
    response = requests.get(url)
    data = response.json()
    share_dict = {}
    data_row = None
    columns = data['marketdata']['columns']
    data_row_list = data['marketdata']['data']
    data_row = data_row_list[0]
    for data_row in data_row_list:
        if "TQBR" in data_row:
            data_row = data_row

    last_price_index = columns.index('LAST')
    market_price_index = columns.index('MARKETPRICE')
    
    last_price = data_row[last_price_index]
    market_price = data_row[market_price_index]
    
    share_dict['last_price'] = last_price
    share_dict['market_price'] = market_price

    if share_dict['last_price']:
        return share_dict['last_price']
    else: 
        return share_dict['market_price']
    

if __name__ == '__main__':
    print(get_last_price("PMSB")) 